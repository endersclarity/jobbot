#!/usr/bin/env node
/**
 * 🔗 LinkedIn Jobs Scraper - Professional Network Job Extraction
 * 
 * Enterprise-grade LinkedIn job scraping using Crawlee framework.
 * Focuses on professional roles with enhanced data extraction.
 */

import { BaseJobScraper } from './base_scraper.js';

export class LinkedInJobScraper extends BaseJobScraper {
    constructor(options = {}) {
        super('linkedin', {
            maxConcurrency: 1, // LinkedIn is strict about rate limiting
            maxRequestsPerCrawl: 25, // Conservative limit for LinkedIn
            requestHandlerTimeoutSecs: 90, // LinkedIn can be slow to load
            ...options
        });
    }

    /**
     * LinkedIn-specific pre-navigation setup
     */
    async preNavigationHook(page) {
        // LinkedIn-specific stealth measures
        await page.addInitScript(() => {
            // Override screen properties to appear more realistic
            Object.defineProperty(screen, 'width', {
                get: () => 1920,
            });
            Object.defineProperty(screen, 'height', {
                get: () => 1080,
            });
            
            // Override timezone to appear consistent
            Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
                value: () => ({
                    calendar: 'gregory',
                    day: '2-digit',
                    locale: 'en-US',
                    month: '2-digit',
                    numberingSystem: 'latn',
                    timeZone: 'America/New_York',
                    year: 'numeric'
                })
            });
        });

        // Set realistic headers for LinkedIn
        await page.setExtraHTTPHeaders({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Dnt': '1',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        });
    }

    /**
     * Extract job data from LinkedIn pages
     */
    async extractJobs(page, request, log) {
        // Wait for LinkedIn's dynamic content to load
        try {
            await page.waitForSelector('.jobs-search__results-list, .jobs-search-results-list', { timeout: 10000 });
        } catch (e) {
            log.warning('[LinkedIn] No job results container found, trying alternative selectors');
        }

        // LinkedIn job selectors (they change these frequently)
        const jobSelectors = [
            '.jobs-search-results__list-item',
            '.job-search-card',
            '.jobs-search-results-list .artdeco-list__item',
            '.scaffold-layout__list-container .artdeco-list__item'
        ];

        let jobElements = [];
        for (const selector of jobSelectors) {
            try {
                jobElements = await page.$$(selector);
                if (jobElements.length > 0) {
                    log.info(`✅ [LinkedIn] Found ${jobElements.length} jobs using selector: ${selector}`);
                    break;
                }
            } catch (e) {
                log.debug(`❌ [LinkedIn] Selector ${selector} failed: ${e.message}`);
            }
        }

        if (jobElements.length === 0) {
            log.warning('[LinkedIn] No job listings found with any selector');
            return [];
        }

        // Extract job data from each job card
        const jobs = [];
        for (const jobElement of jobElements) {
            try {
                const jobData = await jobElement.evaluate((el) => {
                    // Title extraction
                    const titleEl = el.querySelector('.job-search-card__title a, .jobs-unified-top-card__job-title a, h3 a');
                    const title = titleEl?.textContent?.trim();
                    const url = titleEl?.href;

                    // Company extraction  
                    const companyEl = el.querySelector('.job-search-card__subtitle a, .jobs-unified-top-card__company-name a, h4 a');
                    const company = companyEl?.textContent?.trim();
                    const companyUrl = companyEl?.href;

                    // Location extraction
                    const locationEl = el.querySelector('.job-search-card__location, .jobs-unified-top-card__bullet, .job-search-card__metadata-item');
                    const location = locationEl?.textContent?.trim();

                    // Time posted extraction
                    const timeEl = el.querySelector('.job-search-card__listdate, .jobs-unified-top-card__posted-date, time');
                    const postedTime = timeEl?.textContent?.trim() || timeEl?.getAttribute('datetime');

                    // Job insights (salary, applicants, etc.)
                    const insightsEl = el.querySelector('.job-search-card__benefits, .jobs-unified-top-card__job-insight');
                    const insights = insightsEl?.textContent?.trim();

                    // Promoted/sponsored flag
                    const promoted = el.querySelector('.job-search-card__promoted, [data-promoted="true"]') ? true : false;

                    // Easy apply flag
                    const easyApply = el.querySelector('.jobs-apply-button--top-card, [data-easy-apply="true"]') ? true : false;

                    // Job ID extraction from URL or data attributes
                    const jobId = url?.match(/jobs\/view\/(\d+)/)?.[1] || 
                                 el.getAttribute('data-job-id') ||
                                 `linkedin-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

                    return {
                        title,
                        company,
                        location,
                        url,
                        jobId,
                        companyUrl,
                        postedTime,
                        insights,
                        promoted,
                        easyApply
                    };
                });

                if (jobData.title && jobData.company) {
                    jobs.push(jobData);
                }
            } catch (error) {
                log.debug(`[LinkedIn] Error extracting job data: ${error.message}`);
            }
        }

        return jobs;
    }

    /**
     * Build LinkedIn job search URLs
     */
    buildSearchUrls(query, location = '', maxPages = 3) {
        const urls = [];
        const baseUrl = 'https://www.linkedin.com/jobs/search';
        
        for (let page = 0; page < maxPages; page++) {
            const params = new URLSearchParams({
                keywords: query,
                location: location,
                start: page * 25, // LinkedIn shows 25 jobs per page
                sortBy: 'R', // Most recent
                f_TPR: 'r86400' // Posted in last 24 hours (optional)
            });
            
            urls.push(`${baseUrl}?${params.toString()}`);
        }
        
        return urls;
    }

    /**
     * LinkedIn-specific search with professional filters
     */
    async scrapeJobsWithFilters(query, location = '', options = {}) {
        const {
            maxPages = 3,
            experienceLevel = null, // 1=Internship, 2=Entry level, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive
            jobType = null, // F=Full-time, P=Part-time, C=Contract, T=Temporary, I=Internship, V=Volunteer, O=Other
            companySize = null, // B=1-10, C=11-50, D=51-200, E=201-500, F=501-1000, G=1001-5000, H=5001-10000, I=10000+
            datePosted = null, // r86400=Past 24 hours, r604800=Past week, r2592000=Past month
            remote = false,
            salary = null
        } = options;

        const urls = [];
        const baseUrl = 'https://www.linkedin.com/jobs/search';
        
        for (let page = 0; page < maxPages; page++) {
            const params = new URLSearchParams({
                keywords: query,
                location: location,
                start: page * 25,
                sortBy: 'R'
            });
            
            // Add professional filters
            if (experienceLevel) params.append('f_E', experienceLevel);
            if (jobType) params.append('f_JT', jobType);
            if (companySize) params.append('f_C', companySize);
            if (datePosted) params.append('f_TPR', datePosted);
            if (remote) params.append('f_WT', '2'); // Remote work
            if (salary) params.append('f_SB2', salary);
            
            urls.push(`${baseUrl}?${params.toString()}`);
        }

        // Use the base scraping method with custom URLs
        this.stats.startTime = new Date();
        console.log(`🔍 [LinkedIn] Starting professional search for: "${query}" in "${location}"`);
        
        try {
            const crawler = this.createCrawler();
            console.log(`📋 [LinkedIn] Queueing ${urls.length} professional URLs...`);
            
            await crawler.run(urls);
            
            this.stats.endTime = new Date();
            const duration = (this.stats.endTime - this.stats.startTime) / 1000;
            
            console.log(`🎉 [LinkedIn] Professional scraping complete!`);
            console.log(`📊 Stats: ${this.stats.jobsExtracted} jobs, ${duration}s`);
            
            return this.results;
            
        } catch (error) {
            this.stats.endTime = new Date();
            console.error(`❌ [LinkedIn] Professional scraping failed: ${error.message}`);
            throw error;
        }
    }

    /**
     * Enhanced error handling for LinkedIn's anti-bot measures
     */
    async handleLinkedInBlocking(page, log) {
        // Check for LinkedIn challenge pages
        const challengeSelectors = [
            '.challenge-page',
            '.security-challenge-page',
            '[data-test-id="security-challenge"]'
        ];

        for (const selector of challengeSelectors) {
            if (await page.$(selector)) {
                log.warning('[LinkedIn] Detected security challenge - implementing delay');
                await page.waitForTimeout(30000 + Math.random() * 30000); // 30-60 second delay
                return true;
            }
        }

        return false;
    }
}