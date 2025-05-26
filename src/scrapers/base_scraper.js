#!/usr/bin/env node
/**
 * 🏗️ Base Scraper Class - Modular Multi-Site Architecture
 * 
 * Foundation for enterprise-grade job scraping across multiple sites.
 * Each site inherits from this base class for consistent behavior.
 */

import { PlaywrightCrawler } from 'crawlee';

/**
 * Abstract base class for all job site scrapers
 */
export class BaseJobScraper {
    constructor(siteName, options = {}) {
        this.siteName = siteName;
        this.options = {
            maxConcurrency: 1,
            maxRequestsPerCrawl: 50,
            requestHandlerTimeoutSecs: 60,
            headless: true,
            retryAttempts: 3,
            ...options
        };
        
        this.results = [];
        this.stats = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            jobsExtracted: 0,
            startTime: null,
            endTime: null
        };
    }

    /**
     * Generate realistic rotating user agents for anti-detection
     */
    generateRandomUA() {
        const userAgents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ];
        return userAgents[Math.floor(Math.random() * userAgents.length)];
    }

    /**
     * Create enterprise-grade crawler with anti-detection
     * Child classes can override for site-specific configurations
     */
    createCrawler() {
        return new PlaywrightCrawler({
            // Enhanced anti-detection
            launchContext: {
                launchOptions: {
                    headless: this.options.headless,
                    args: [
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-blink-features=AutomationControlled',
                        `--user-agent=${this.generateRandomUA()}`
                    ]
                }
            },
            
            // Stealth measures
            preNavigationHooks: [
                async ({ page }) => {
                    // Remove webdriver property
                    await page.addInitScript(() => {
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined,
                        });
                    });
                    
                    // Add realistic viewport and headers
                    await page.setViewportSize({ width: 1366, height: 768 });
                    await page.setExtraHTTPHeaders({
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Upgrade-Insecure-Requests': '1'
                    });
                    
                    // Call site-specific pre-navigation hooks
                    await this.preNavigationHook(page);
                }
            ],

            // Crawlee configuration  
            maxConcurrency: this.options.maxConcurrency,
            maxRequestsPerCrawl: this.options.maxRequestsPerCrawl,
            requestHandlerTimeoutSecs: this.options.requestHandlerTimeoutSecs,

            // Main scraping logic with error handling
            async requestHandler({ request, page, pushData, log }) {
                this.stats.totalRequests++;
                log.info(`🎯 [${this.siteName}] Scraping: ${request.url}`);

                try {
                    // Random delay to appear more human
                    await page.waitForTimeout(Math.random() * 2000 + 1000);
                    
                    // Call site-specific scraping logic
                    const jobsRaw = await this.extractJobs(page, request, log) || [];
                    const jobs = Array.isArray(jobsRaw) ? jobsRaw : [jobsRaw];
                    
                    // Save results
                    for (const job of jobs) {
                        // Add metadata
                        job.source = this.siteName;
                        job.scrapedAt = new Date().toISOString();
                        job.scrapedBy = 'crawlee-multi-site';
                        
                        await pushData(job);
                        this.results.push(job);
                    }

                    this.stats.successfulRequests++;
                    this.stats.jobsExtracted += jobs.length;
                    log.info(`✅ [${this.siteName}] Extracted ${jobs.length} jobs from ${request.url}`);

                } catch (error) {
                    this.stats.failedRequests++;
                    log.error(`❌ [${this.siteName}] Error scraping ${request.url}: ${error.message}`);
                    
                    // Retry logic
                    if (request.retryCount < this.options.retryAttempts) {
                        log.info(`🔄 [${this.siteName}] Retrying ${request.url} (attempt ${request.retryCount + 1})`);
                        throw error; // Crawlee will handle retry
                    }
                }
            },

            // Error handling
            async failedRequestHandler({ request, log }) {
                log.error(`💥 [${this.siteName}] Failed to scrape after ${this.options.retryAttempts} attempts: ${request.url}`);
            }
        });
    }

    /**
     * Site-specific pre-navigation hook (override in child classes)
     */
    async preNavigationHook(page) {
        // Default implementation - can be overridden
    }

    /**
     * Abstract method - must be implemented by child classes
     */
    async extractJobs(page, request, log) {
        throw new Error(`extractJobs() must be implemented by ${this.siteName} scraper`);
    }

    /**
     * Abstract method - must be implemented by child classes
     */
    buildSearchUrls(query, location, maxPages) {
        throw new Error(`buildSearchUrls() must be implemented by ${this.siteName} scraper`);
    }

    /**
     * Execute the scraping with comprehensive error handling
     */
    async scrapeJobs(query, location = '', maxPages = 3) {
        this.stats.startTime = new Date();
        console.log(`🔍 [${this.siteName}] Starting scrape for: "${query}" in "${location}"`);
        
        try {
            const crawler = this.createCrawler();
            const urls = this.buildSearchUrls(query, location, maxPages);
            
            console.log(`📋 [${this.siteName}] Queueing ${urls.length} URLs for extraction...`);
            
            // Execute the scraping
            await crawler.run(urls);
            
            this.stats.endTime = new Date();
            const duration = (this.stats.endTime - this.stats.startTime) / 1000;
            
            console.log(`🎉 [${this.siteName}] Scraping complete!`);
            console.log(`📊 Stats: ${this.stats.jobsExtracted} jobs, ${duration}s, ${this.stats.successfulRequests}/${this.stats.totalRequests} requests successful`);
            
            return this.results;
            
        } catch (error) {
            this.stats.endTime = new Date();
            console.error(`❌ [${this.siteName}] Scraping failed: ${error.message}`);
            throw error;
        }
    }

    /**
     * Get scraping statistics
     */
    getStats() {
        const duration = this.stats.endTime ? 
            (this.stats.endTime - this.stats.startTime) / 1000 : 0;
            
        return {
            ...this.stats,
            siteName: this.siteName,
            duration,
            successRate: this.stats.totalRequests > 0 ? 
                (this.stats.successfulRequests / this.stats.totalRequests * 100).toFixed(2) : 0,
            jobsPerSecond: duration > 0 ? 
                (this.stats.jobsExtracted / duration).toFixed(2) : 0
        };
    }

    /**
     * Reset scraper state for new run
     */
    reset() {
        this.results = [];
        this.stats = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            jobsExtracted: 0,
            startTime: null,
            endTime: null
        };
    }
}