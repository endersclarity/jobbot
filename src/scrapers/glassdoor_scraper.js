#!/usr/bin/env node
/**
 * 🏢 Glassdoor Jobs Scraper - Salary-Focused Job Extraction
 * 
 * Enterprise-grade Glassdoor job scraping with enhanced salary data extraction.
 * Focuses on compensation transparency and company insights.
 */

import { BaseJobScraper } from './base_scraper.js';

export class GlassdoorJobScraper extends BaseJobScraper {
    constructor(options = {}) {
        super('glassdoor', {
            maxConcurrency: 1, // Glassdoor is very strict about rate limiting
            maxRequestsPerCrawl: 20, // Conservative limit for Glassdoor
            requestHandlerTimeoutSecs: 120, // Glassdoor can be very slow
            ...options
        });
    }

    /**
     * Glassdoor-specific pre-navigation setup
     */
    async preNavigationHook(page) {
        // Glassdoor-specific stealth measures
        await page.addInitScript(() => {
            // Override permissions API to avoid detection
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' })
                })
            });
            
            // Override connection info
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    downlink: 10,
                    effectiveType: '4g',
                    rtt: 50,
                    saveData: false
                })
            });

            // Override hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
        });

        // Set Glassdoor-specific headers
        await page.setExtraHTTPHeaders({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Dnt': '1',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Google Chrome";v="121", "Not A(Brand";v="99", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        });
    }

    /**
     * Extract job data from Glassdoor pages with enhanced salary extraction
     */
    async extractJobs(page, request, log) {
        // Wait for Glassdoor's dynamic content to load
        try {
            await page.waitForSelector('[data-test="job-search-results"], .react-job-listing, .jobListing', { timeout: 15000 });
        } catch (e) {
            log.warning('[Glassdoor] No job results container found, trying alternative approach');
        }

        // Handle Glassdoor's signup prompts
        await this.handleSignupPrompts(page, log);

        // Glassdoor job selectors
        const jobSelectors = [
            '[data-test="job-search-results"] > div',
            '.react-job-listing',
            '.jobListing',
            '.job-search-card',
            '[data-id^="job_"]'
        ];

        let jobElements = [];
        for (const selector of jobSelectors) {
            try {
                jobElements = await page.$$(selector);
                if (jobElements.length > 0) {
                    log.info(`✅ [Glassdoor] Found ${jobElements.length} jobs using selector: ${selector}`);
                    break;
                }
            } catch (e) {
                log.debug(`❌ [Glassdoor] Selector ${selector} failed: ${e.message}`);
            }
        }

        if (jobElements.length === 0) {
            log.warning('[Glassdoor] No job listings found with any selector');
            return [];
        }

        // Extract job data with focus on salary information
        const jobs = [];
        for (const jobElement of jobElements) {
            try {
                const jobData = await jobElement.evaluate((el) => {
                    // Title extraction
                    const titleEl = el.querySelector('[data-test="job-title"] a, .jobTitle a, h2 a, h3 a');
                    const title = titleEl?.textContent?.trim();
                    const url = titleEl?.href;

                    // Company extraction
                    const companyEl = el.querySelector('[data-test="employer-name"], .employerName, .employer a');
                    const company = companyEl?.textContent?.trim();

                    // Location extraction
                    const locationEl = el.querySelector('[data-test="job-location"], .location, .jobLocation');
                    const location = locationEl?.textContent?.trim();

                    // Salary extraction (Glassdoor's key feature)
                    const salarySelectors = [
                        '[data-test="salary-estimate"]',
                        '.salaryText',
                        '.salary-estimate',
                        '.sal-wrap',
                        '.css-1uunp2d'
                    ];
                    let salary = null;
                    for (const selector of salarySelectors) {
                        const salaryEl = el.querySelector(selector);
                        if (salaryEl) {
                            salary = salaryEl.textContent?.trim();
                            break;
                        }
                    }

                    // Company rating extraction
                    const ratingEl = el.querySelector('[data-test="rating"], .rating, .companyRating');
                    const rating = ratingEl?.textContent?.trim();

                    // Job age/posted date
                    const dateEl = el.querySelector('[data-test="job-age"], .jobAge, time');
                    const postedDate = dateEl?.textContent?.trim() || dateEl?.getAttribute('datetime');

                    // Job type/benefits
                    const benefitsEl = el.querySelector('[data-test="job-benefits"], .benefits, .jobBenefits');
                    const benefits = benefitsEl?.textContent?.trim();

                    // Easy apply detection
                    const easyApply = el.querySelector('[data-test="easy-apply"], .easyApply, .apply-btn') ? true : false;

                    // Sponsored job detection
                    const sponsored = el.querySelector('[data-test="sponsored"], .sponsoredJob, .sponsored') ? true : false;

                    // Job ID extraction
                    const jobId = url?.match(/job-listing\/([^/?]+)/)?.[1] || 
                                 el.getAttribute('data-id') ||
                                 el.getAttribute('data-job-id') ||
                                 `glassdoor-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

                    // Company size information
                    const companySizeEl = el.querySelector('[data-test="company-size"], .companySize');
                    const companySize = companySizeEl?.textContent?.trim();

                    // Industry information
                    const industryEl = el.querySelector('[data-test="industry"], .industry');
                    const industry = industryEl?.textContent?.trim();

                    return {
                        title,
                        company,
                        location,
                        url,
                        jobId,
                        salary,
                        rating,
                        postedDate,
                        benefits,
                        easyApply,
                        sponsored,
                        companySize,
                        industry
                    };
                });

                if (jobData.title && jobData.company) {
                    jobs.push(jobData);
                }
            } catch (error) {
                log.debug(`[Glassdoor] Error extracting job data: ${error.message}`);
            }
        }

        return jobs;
    }

    /**
     * Build Glassdoor job search URLs
     */
    buildSearchUrls(query, location = '', maxPages = 3) {
        const urls = [];
        const baseUrl = 'https://www.glassdoor.com/Job/jobs.htm';
        
        for (let page = 1; page <= maxPages; page++) {
            const params = new URLSearchParams({
                sc: 'fq', // SearchContext
                kw: query, // Keywords
                locT: 'C', // Location Type (City)
                locId: '1147401', // Default to San Francisco area
                p: page.toString()
            });
            
            if (location) {
                // For simplicity, we'll use the location as-is
                // In production, you'd want to map locations to Glassdoor's location IDs
                params.set('locKeyword', location);
            }
            
            urls.push(`${baseUrl}?${params.toString()}`);
        }
        
        return urls;
    }

    /**
     * Glassdoor-specific search with salary and company filters
     */
    async scrapeJobsWithFilters(query, location = '', options = {}) {
        const {
            maxPages = 3,
            minSalary = null,
            maxSalary = null,
            companyType = null, // 'startup', 'nonprofit', 'public', 'private'
            companySize = null, // '1-50', '51-200', '201-500', '501-1000', '1001-5000', '5000+'
            jobType = null, // 'fulltime', 'parttime', 'contract', 'internship'
            datePosted = null, // '1', '7', '14', '30' (days)
            remote = false
        } = options;

        const urls = [];
        const baseUrl = 'https://www.glassdoor.com/Job/jobs.htm';
        
        for (let page = 1; page <= maxPages; page++) {
            const params = new URLSearchParams({
                sc: 'fq',
                kw: query,
                locT: 'C',
                locId: '1147401',
                p: page.toString()
            });
            
            if (location) params.set('locKeyword', location);
            
            // Add salary filters
            if (minSalary) params.append('minSalary', minSalary);
            if (maxSalary) params.append('maxSalary', maxSalary);
            
            // Add company filters
            if (companyType) params.append('companyType', companyType);
            if (companySize) params.append('companySize', companySize);
            
            // Add job type filter
            if (jobType) params.append('jobType', jobType);
            
            // Add date filter
            if (datePosted) params.append('fromAge', datePosted);
            
            // Add remote work filter
            if (remote) params.append('remoteWorkType', '1');
            
            urls.push(`${baseUrl}?${params.toString()}`);
        }

        // Execute filtered search
        this.stats.startTime = new Date();
        console.log(`🔍 [Glassdoor] Starting salary-focused search for: "${query}" in "${location}"`);
        
        try {
            const crawler = this.createCrawler();
            console.log(`📋 [Glassdoor] Queueing ${urls.length} salary-focused URLs...`);
            
            await crawler.run(urls);
            
            this.stats.endTime = new Date();
            const duration = (this.stats.endTime - this.stats.startTime) / 1000;
            
            console.log(`🎉 [Glassdoor] Salary-focused scraping complete!`);
            console.log(`📊 Stats: ${this.stats.jobsExtracted} jobs, ${duration}s`);
            
            return this.results;
            
        } catch (error) {
            this.stats.endTime = new Date();
            console.error(`❌ [Glassdoor] Salary-focused scraping failed: ${error.message}`);
            throw error;
        }
    }

    /**
     * Handle Glassdoor's signup prompts and overlays
     */
    async handleSignupPrompts(page, log) {
        const signupSelectors = [
            '.signup-modal',
            '.hardsell-modal',
            '[data-test="signup-modal"]',
            '.modal-content',
            '.overlay-content'
        ];

        for (const selector of signupSelectors) {
            try {
                const modal = await page.$(selector);
                if (modal) {
                    log.info('[Glassdoor] Detected signup modal, attempting to close');
                    
                    // Try to find and click close button
                    const closeSelectors = [
                        '.close-btn',
                        '.modal-close',
                        '[data-test="close-button"]',
                        '.btn-close',
                        'button[aria-label="Close"]'
                    ];
                    
                    for (const closeSelector of closeSelectors) {
                        const closeBtn = await page.$(closeSelector);
                        if (closeBtn) {
                            await closeBtn.click();
                            await page.waitForTimeout(2000);
                            log.info('[Glassdoor] Closed signup modal');
                            return;
                        }
                    }
                    
                    // If no close button found, try pressing Escape
                    await page.keyboard.press('Escape');
                    await page.waitForTimeout(2000);
                }
            } catch (e) {
                log.debug(`[Glassdoor] Error handling signup prompt: ${e.message}`);
            }
        }
    }

    /**
     * Extract additional company insights available on Glassdoor
     */
    async extractCompanyInsights(page, companyName, log) {
        try {
            // Navigate to company overview page
            const companyUrl = `https://www.glassdoor.com/Overview/Working-at-${companyName.replace(/\s+/g, '-')}-EI_IE.htm`;
            await page.goto(companyUrl, { waitUntil: 'networkidle2', timeout: 30000 });
            
            // Extract company insights
            const insights = await page.evaluate(() => {
                const rating = document.querySelector('.rating')?.textContent?.trim();
                const reviewCount = document.querySelector('.review-count')?.textContent?.trim();
                const ceoApproval = document.querySelector('.ceo-approval')?.textContent?.trim();
                const wouldRecommend = document.querySelector('.recommend-percent')?.textContent?.trim();
                
                return {
                    rating,
                    reviewCount,
                    ceoApproval,
                    wouldRecommend
                };
            });
            
            log.info(`[Glassdoor] Extracted company insights for ${companyName}`);
            return insights;
            
        } catch (error) {
            log.warning(`[Glassdoor] Could not extract company insights for ${companyName}: ${error.message}`);
            return null;
        }
    }
}