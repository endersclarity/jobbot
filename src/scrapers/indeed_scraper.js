#!/usr/bin/env node
/**
 * 🎯 Indeed Job Scraper - Modular Architecture
 * 
 * Refactored Indeed scraper using the new base class architecture.
 * Maintains all existing functionality while adding modularity.
 */

import { BaseJobScraper } from './base_scraper.js';

export class IndeedJobScraper extends BaseJobScraper {
    constructor(options = {}) {
        super('indeed', {
            maxConcurrency: 1, // Respectful scraping
            maxRequestsPerCrawl: 50,
            requestHandlerTimeoutSecs: 60,
            ...options
        });
    }

    /**
     * Indeed-specific pre-navigation setup
     */
    async preNavigationHook(page) {
        // Indeed-specific stealth measures
        await page.addInitScript(() => {
            // Override plugins length to avoid detection
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override languages to appear more realistic
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        });
    }

    /**
     * Extract job data from Indeed pages
     */
    async extractJobs(page, request, log) {
        // Try multiple selectors for job listings (Indeed changes these frequently)
        const selectors = [
            '[data-testid="job-title"]',
            '.jobTitle a',
            '[data-jk] h2 a',
            '.jobTitle',
            '[data-cy="job-title"]'
        ];
        
        let jobSelector = null;
        for (const selector of selectors) {
            try {
                await page.waitForSelector(selector, { timeout: 5000 });
                jobSelector = selector;
                log.info(`✅ [Indeed] Found jobs using selector: ${selector}`);
                break;
            } catch (e) {
                log.debug(`❌ [Indeed] Selector ${selector} not found`);
            }
        }
        
        if (!jobSelector) {
            log.warning('[Indeed] No job listings found with any selector');
            return [];
        }

        // Extract job data using found selector
        const jobs = await page.$$eval(jobSelector, (elements) => {
            return elements.map(el => {
                const jobCard = el.closest('[data-jk], .job_seen_beacon, .jobsearch-SerpJobCard, .result');
                
                // Extract salary information
                const salaryElement = jobCard?.querySelector('[data-testid="job-salary"], .salaryText, .salary-snippet');
                const salary = salaryElement?.textContent?.trim();
                
                // Extract job type/schedule
                const jobTypeElement = jobCard?.querySelector('[data-testid="job-type"], .jobMetadataHeader, .jobMetadata');
                const jobType = jobTypeElement?.textContent?.trim();
                
                // Extract posting date
                const dateElement = jobCard?.querySelector('[data-testid="job-age"], .date, .jobMetadata span');
                const postedDate = dateElement?.textContent?.trim();
                
                return {
                    title: el.textContent?.trim() || el.getAttribute('title')?.trim(),
                    company: jobCard?.querySelector('[data-testid="company-name"], .companyName, [data-testid="company-name"] span')?.textContent?.trim(),
                    location: jobCard?.querySelector('[data-testid="job-location"], .companyLocation, .locationsContainer')?.textContent?.trim(),
                    url: el.href || window.location.origin + el.getAttribute('href'),
                    jobKey: jobCard?.getAttribute('data-jk') || `indeed-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                    summary: jobCard?.querySelector('[data-testid="job-snippet"], .summary, .jobSnippet')?.textContent?.trim(),
                    salary: salary,
                    jobType: jobType,
                    postedDate: postedDate,
                    // Indeed-specific metadata
                    sponsored: jobCard?.querySelector('.sponsoredJob, [data-testid="sponsored-job"]') ? true : false,
                    easyApply: jobCard?.querySelector('.indeedApply, [data-testid="easy-apply"]') ? true : false
                };
            }).filter(job => job.title); // Only include jobs with titles
        });

        return jobs;
    }

    /**
     * Build Indeed search URLs
     */
    buildSearchUrls(query, location = '', maxPages = 3) {
        const urls = [];
        const baseUrl = 'https://www.indeed.com/jobs';
        
        for (let page = 0; page < maxPages; page++) {
            const params = new URLSearchParams({
                q: query,
                l: location,
                start: page * 10
            });
            
            urls.push(`${baseUrl}?${params.toString()}`);
        }
        
        return urls;
    }

    /**
     * Indeed-specific search with additional parameters
     */
    async scrapeJobsWithFilters(query, location = '', options = {}) {
        const {
            maxPages = 3,
            salary = null,
            jobType = null,
            datePosted = null,
            experienceLevel = null,
            remote = false
        } = options;

        // Build URLs with filters
        const urls = [];
        const baseUrl = 'https://www.indeed.com/jobs';
        
        for (let page = 0; page < maxPages; page++) {
            const params = new URLSearchParams({
                q: query,
                l: location,
                start: page * 10
            });
            
            // Add filters if specified
            if (salary) params.append('salary', salary);
            if (jobType) params.append('jt', jobType);
            if (datePosted) params.append('fromage', datePosted);
            if (experienceLevel) params.append('explvl', experienceLevel);
            if (remote) params.append('remotejob', '1');
            
            urls.push(`${baseUrl}?${params.toString()}`);
        }

        // Use the base scraping method with custom URLs
        this.stats.startTime = new Date();
        console.log(`🔍 [Indeed] Starting filtered scrape for: "${query}" in "${location}"`);
        
        try {
            const crawler = this.createCrawler();
            console.log(`📋 [Indeed] Queueing ${urls.length} filtered URLs...`);
            
            await crawler.run(urls);
            
            this.stats.endTime = new Date();
            const duration = (this.stats.endTime - this.stats.startTime) / 1000;
            
            console.log(`🎉 [Indeed] Filtered scraping complete!`);
            console.log(`📊 Stats: ${this.stats.jobsExtracted} jobs, ${duration}s`);
            
            return this.results;
            
        } catch (error) {
            this.stats.endTime = new Date();
            console.error(`❌ [Indeed] Filtered scraping failed: ${error.message}`);
            throw error;
        }
    }
}