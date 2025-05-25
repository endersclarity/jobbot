#!/usr/bin/env node
/**
 * 🎼 Multi-Site Scraping Orchestrator - Enterprise Coordination Engine
 * 
 * Coordinates concurrent scraping across multiple job sites with:
 * - Parallel execution management
 * - Circuit breaker pattern for reliability
 * - Real-time metrics and monitoring
 * - Advanced error recovery and retry logic
 */

import { parseArgs } from 'util';
import { IndeedJobScraper } from './scrapers/indeed_scraper.js';
import { LinkedInJobScraper } from './scrapers/linkedin_scraper.js';
import { GlassdoorJobScraper } from './scrapers/glassdoor_scraper.js';

/**
 * Circuit breaker states for site reliability management
 */
const CircuitState = {
    CLOSED: 'closed',     // Normal operation
    OPEN: 'open',         // Failing, stop requests
    HALF_OPEN: 'half_open' // Testing if recovered
};

/**
 * Multi-site job scraping orchestrator with enterprise features
 */
export class MultiSiteOrchestrator {
    constructor(options = {}) {
        this.options = {
            maxConcurrency: 3,           // Max simultaneous site scrapers
            globalTimeout: 600000,       // 10 minute global timeout
            retryAttempts: 2,            // Retry failed sites
            circuitBreakerThreshold: 3,  // Failures before opening circuit
            circuitBreakerTimeout: 300000, // 5 minute circuit breaker timeout
            ...options
        };

        // Initialize scrapers
        this.scrapers = new Map([
            ['indeed', new IndeedJobScraper()],
            ['linkedin', new LinkedInJobScraper()],
            ['glassdoor', new GlassdoorJobScraper()]
        ]);

        // Circuit breaker state management
        this.circuitBreakers = new Map();
        this.initializeCircuitBreakers();

        // Global metrics
        this.globalStats = {
            startTime: null,
            endTime: null,
            totalJobs: 0,
            totalSites: 0,
            successfulSites: 0,
            failedSites: 0,
            siteResults: new Map()
        };
    }

    /**
     * Initialize circuit breakers for all scrapers
     */
    initializeCircuitBreakers() {
        for (const [siteName] of this.scrapers) {
            this.circuitBreakers.set(siteName, {
                state: CircuitState.CLOSED,
                failures: 0,
                lastFailureTime: null,
                successes: 0
            });
        }
    }

    /**
     * Check if a site's circuit breaker allows requests
     */
    canExecuteSite(siteName) {
        const breaker = this.circuitBreakers.get(siteName);
        if (!breaker) return true;

        switch (breaker.state) {
            case CircuitState.CLOSED:
                return true;
                
            case CircuitState.OPEN:
                // Check if enough time has passed to try half-open
                const timeSinceFailure = Date.now() - breaker.lastFailureTime;
                if (timeSinceFailure >= this.options.circuitBreakerTimeout) {
                    breaker.state = CircuitState.HALF_OPEN;
                    console.log(`🔄 [${siteName}] Circuit breaker moving to HALF_OPEN for testing`);
                    return true;
                }
                return false;
                
            case CircuitState.HALF_OPEN:
                return true;
                
            default:
                return true;
        }
    }

    /**
     * Record success for circuit breaker
     */
    recordSuccess(siteName) {
        const breaker = this.circuitBreakers.get(siteName);
        if (!breaker) return;

        breaker.successes++;
        
        if (breaker.state === CircuitState.HALF_OPEN) {
            // Recovered! Reset to closed
            breaker.state = CircuitState.CLOSED;
            breaker.failures = 0;
            breaker.successes = 0;
            console.log(`✅ [${siteName}] Circuit breaker CLOSED - site recovered`);
        }
    }

    /**
     * Record failure for circuit breaker
     */
    recordFailure(siteName) {
        const breaker = this.circuitBreakers.get(siteName);
        if (!breaker) return;

        breaker.failures++;
        breaker.lastFailureTime = Date.now();

        // Open circuit if threshold exceeded
        if (breaker.failures >= this.options.circuitBreakerThreshold) {
            breaker.state = CircuitState.OPEN;
            console.log(`🚫 [${siteName}] Circuit breaker OPEN - too many failures (${breaker.failures})`);
        }
    }

    /**
     * Execute scraping for a single site with error handling
     */
    async executeSiteScraping(siteName, searchTerm, location, maxJobs) {
        const scraper = this.scrapers.get(siteName);
        if (!scraper) {
            throw new Error(`Unknown scraper: ${siteName}`);
        }

        // Check circuit breaker
        if (!this.canExecuteSite(siteName)) {
            const breaker = this.circuitBreakers.get(siteName);
            const timeUntilRetry = Math.ceil((this.options.circuitBreakerTimeout - (Date.now() - breaker.lastFailureTime)) / 1000);
            throw new Error(`Circuit breaker OPEN - retry in ${timeUntilRetry}s`);
        }

        let attempt = 0;
        while (attempt <= this.options.retryAttempts) {
            try {
                console.log(`🚀 [${siteName}] Starting scraping (attempt ${attempt + 1}/${this.options.retryAttempts + 1})`);
                
                // Reset scraper state
                scraper.reset();
                
                // Execute scraping
                const maxPages = Math.ceil(maxJobs / 25); // Estimate pages needed
                const results = await scraper.scrapeJobs(searchTerm, location, maxPages);
                
                // Record success
                this.recordSuccess(siteName);
                
                return {
                    siteName,
                    success: true,
                    jobs: results,
                    stats: scraper.getStats(),
                    attempt: attempt + 1
                };
                
            } catch (error) {
                attempt++;
                console.error(`❌ [${siteName}] Attempt ${attempt} failed: ${error.message}`);
                
                if (attempt > this.options.retryAttempts) {
                    // All attempts failed - record failure
                    this.recordFailure(siteName);
                    
                    return {
                        siteName,
                        success: false,
                        error: error.message,
                        stats: scraper.getStats(),
                        attempt
                    };
                }
                
                // Wait before retry with exponential backoff
                const backoffDelay = Math.min(1000 * Math.pow(2, attempt - 1), 30000);
                console.log(`⏳ [${siteName}] Waiting ${backoffDelay}ms before retry...`);
                await new Promise(resolve => setTimeout(resolve, backoffDelay));
            }
        }
    }

    /**
     * Execute parallel scraping across multiple sites
     */
    async scrapeAllSites(searchTerm, location = '', options = {}) {
        const {
            sites = ['indeed', 'linkedin', 'glassdoor'],
            maxJobsPerSite = 50,
            jsonOutput = false
        } = options;

        this.globalStats.startTime = new Date();
        this.globalStats.totalSites = sites.length;

        if (!jsonOutput) {
            console.log('\n🎼 MULTI-SITE ORCHESTRATOR INITIATED');
            console.log(`🎯 Target: "${searchTerm}" in "${location}"`);
            console.log(`🌐 Sites: ${sites.join(', ')}`);
            console.log(`📊 Max jobs per site: ${maxJobsPerSite}`);
            console.log(`⚡ Max concurrency: ${this.options.maxConcurrency}\n`);
        }

        // Filter sites based on circuit breaker status
        const availableSites = sites.filter(site => {
            const canExecute = this.canExecuteSite(site);
            if (!canExecute) {
                console.log(`⏭️  [${site}] Skipped - circuit breaker OPEN`);
            }
            return canExecute;
        });

        if (availableSites.length === 0) {
            throw new Error('No sites available - all circuit breakers are OPEN');
        }

        // Execute scraping with concurrency control
        const results = [];
        const semaphore = new Semaphore(this.options.maxConcurrency);
        
        const promises = availableSites.map(async (siteName) => {
            await semaphore.acquire();
            try {
                return await this.executeSiteScraping(siteName, searchTerm, location, maxJobsPerSite);
            } finally {
                semaphore.release();
            }
        });

        // Wait for all scrapers to complete
        const siteResults = await Promise.allSettled(promises);

        // Process results
        for (const result of siteResults) {
            if (result.status === 'fulfilled') {
                const siteResult = result.value;
                results.push(siteResult);
                this.globalStats.siteResults.set(siteResult.siteName, siteResult);
                
                if (siteResult.success) {
                    this.globalStats.successfulSites++;
                    this.globalStats.totalJobs += siteResult.jobs.length;
                } else {
                    this.globalStats.failedSites++;
                }
            } else {
                console.error(`💥 Unexpected orchestrator error: ${result.reason.message}`);
                this.globalStats.failedSites++;
            }
        }

        this.globalStats.endTime = new Date();
        const duration = (this.globalStats.endTime - this.globalStats.startTime) / 1000;

        // Output results
        if (jsonOutput) {
            return this.formatJsonOutput(searchTerm, location, results, duration);
        } else {
            this.displayResults(searchTerm, location, results, duration);
            return results;
        }
    }

    /**
     * Format results as JSON for API integration
     */
    formatJsonOutput(searchTerm, location, results, duration) {
        const allJobs = [];
        const siteStats = {};

        for (const siteResult of results) {
            siteStats[siteResult.siteName] = {
                success: siteResult.success,
                jobCount: siteResult.success ? siteResult.jobs.length : 0,
                stats: siteResult.stats,
                error: siteResult.error || null
            };

            if (siteResult.success) {
                allJobs.push(...siteResult.jobs);
            }
        }

        return {
            success: true,
            searchTerm,
            location,
            totalJobs: allJobs.length,
            duration,
            sitesQueried: results.length,
            sitesSuccessful: this.globalStats.successfulSites,
            siteStats,
            jobs: allJobs,
            orchestratorStats: this.globalStats,
            scrapedAt: new Date().toISOString()
        };
    }

    /**
     * Display comprehensive results summary
     */
    displayResults(searchTerm, location, results, duration) {
        console.log('\n🎉 MULTI-SITE ORCHESTRATION COMPLETE!\n');
        
        // Overall stats
        console.log('📊 OVERALL RESULTS:');
        console.log(`   ✅ Total jobs extracted: ${this.globalStats.totalJobs}`);
        console.log(`   🌐 Sites successful: ${this.globalStats.successfulSites}/${this.globalStats.totalSites}`);
        console.log(`   ⏱️  Total duration: ${duration.toFixed(2)}s`);
        console.log(`   ⚡ Jobs per second: ${(this.globalStats.totalJobs / duration).toFixed(2)}`);

        // Per-site breakdown
        console.log('\n📋 PER-SITE BREAKDOWN:');
        for (const siteResult of results) {
            const status = siteResult.success ? '✅' : '❌';
            const jobCount = siteResult.success ? siteResult.jobs.length : 0;
            const siteTime = siteResult.stats?.duration || 0;
            
            console.log(`   ${status} [${siteResult.siteName}] ${jobCount} jobs in ${siteTime}s`);
            
            if (!siteResult.success) {
                console.log(`      Error: ${siteResult.error}`);
            }
        }

        // Circuit breaker status
        console.log('\n🔌 CIRCUIT BREAKER STATUS:');
        for (const [siteName, breaker] of this.circuitBreakers) {
            const status = breaker.state === CircuitState.CLOSED ? '🟢' : 
                          breaker.state === CircuitState.HALF_OPEN ? '🟡' : '🔴';
            console.log(`   ${status} [${siteName}] ${breaker.state.toUpperCase()} (failures: ${breaker.failures})`);
        }

        // Economic impact
        const costPerJob = 0.03; // Apify's approximate cost per job
        const totalSavings = this.globalStats.totalJobs * costPerJob;
        console.log(`\n💰 ECONOMIC IMPACT:`);
        console.log(`   🆓 Our cost: $0.00`);
        console.log(`   💸 Apify equivalent: $${totalSavings.toFixed(2)}`);
        console.log(`   🔥 LUNCH EATEN: 🍽️💀`);
    }

    /**
     * Get current orchestrator status
     */
    getStatus() {
        return {
            globalStats: this.globalStats,
            circuitBreakers: Object.fromEntries(this.circuitBreakers),
            availableScrapers: Array.from(this.scrapers.keys()),
            configuration: this.options
        };
    }
}

/**
 * Semaphore for concurrency control
 */
class Semaphore {
    constructor(permits) {
        this.permits = permits;
        this.waiting = [];
    }

    async acquire() {
        if (this.permits > 0) {
            this.permits--;
            return;
        }

        return new Promise(resolve => {
            this.waiting.push(resolve);
        });
    }

    release() {
        this.permits++;
        if (this.waiting.length > 0) {
            const next = this.waiting.shift();
            this.permits--;
            next();
        }
    }
}

// CLI execution
async function main() {
    const { values: args } = parseArgs({
        options: {
            search: { type: 'string', default: 'software engineer' },
            location: { type: 'string', default: 'San Francisco, CA' },
            sites: { type: 'string', default: 'indeed,linkedin,glassdoor' },
            max: { type: 'string', default: '50' },
            json: { type: 'boolean', default: false },
            concurrency: { type: 'string', default: '3' }
        }
    });

    const orchestrator = new MultiSiteOrchestrator({
        maxConcurrency: parseInt(args.concurrency, 10)
    });

    try {
        const sites = args.sites.split(',').map(s => s.trim());
        const maxJobs = parseInt(args.max, 10);

        const results = await orchestrator.scrapeAllSites(args.search, args.location, {
            sites,
            maxJobsPerSite: maxJobs,
            jsonOutput: args.json
        });

        if (args.json) {
            console.log(JSON.stringify(results, null, 2));
        }

    } catch (error) {
        if (args.json) {
            console.log(JSON.stringify({
                success: false,
                error: error.message,
                searchTerm: args.search,
                location: args.location,
                scrapedAt: new Date().toISOString()
            }, null, 2));
            process.exit(1);
        } else {
            console.error(`❌ Orchestration failed: ${error.message}`);
            process.exit(1);
        }
    }
}

// Execute if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}