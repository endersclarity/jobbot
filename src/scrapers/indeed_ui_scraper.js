/**
 * Indeed UI Navigation Scraper
 * 
 * Implements the comprehensive Indeed UI navigation strategy to bypass anti-scraping measures
 * through Browser MCP automation with human-like behavior patterns.
 * 
 * Based on strategy document: indeed_ui_navigation_strategy.md
 */

import { PlaywrightCrawler } from 'crawlee';
import { randomUserAgent } from 'random-useragent';

class IndeedUINavigationScraper {
    constructor(options = {}) {
        this.options = {
            maxConcurrency: 2,
            requestDelay: 2000,
            headless: false, // Visible browser for better detection avoidance
            ...options
        };
        
        // Anti-detection configuration
        this.userAgents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ];
        
        // Search form selectors (with fallbacks)
        this.selectors = {
            // Primary search form selectors
            searchForm: 'form[role="search"], .jobsearch-SerpFilters form, #searchform',
            keywordsInput: 'input[name="q"], input[aria-label*="job title"], input[placeholder*="job title"], #text-input-what',
            locationInput: 'input[name="l"], input[aria-label*="location"], input[placeholder*="location"], #text-input-where',
            searchButton: 'button[type="submit"], .yosegi-InlineWhatWhere-primaryButton, input[type="submit"]',
            
            // Job results selectors
            jobCards: '.jobsearch-SerpJobCard, .slider_container .slider_item, [data-testid="job-card"]',
            jobTitle: '.jobTitle a, .jobTitle-color-purple, h2 a[data-testid="job-title"]',
            companyName: '.companyName, .company, [data-testid="company-name"]',
            location: '.companyLocation, .location, [data-testid="job-location"]',
            salary: '.salaryText, .salary-snippet, [data-testid="job-salary"]',
            summary: '.summary, .job-snippet, [data-testid="job-summary"]',
            
            // Pagination selectors
            nextPage: 'a[aria-label="Next Page"], a[aria-label="Next"], .np:last-child',
            
            // Challenge detection selectors
            captcha: '.cf-challenge-form, .challenge-form, #captcha',
            blocked: '.blocked, .access-denied, .cf-error-title',
            
            // Alternative selectors for resilience
            altJobCards: '.result, .jobsearch-result, [data-jk]',
            altJobTitle: 'h2 a, .jobtitle, [data-testid="job-title"] span',
            altCompanyName: '[data-testid="company-name"] span, .company span',
            altLocation: '[data-testid="job-location"] div'
        };
        
        // Geographic search configuration
        this.searchRegions = [
            { location: 'San Francisco, CA', keywords: 'software engineer' },
            { location: 'New York, NY', keywords: 'data scientist' },
            { location: 'Seattle, WA', keywords: 'product manager' },
            { location: 'Austin, TX', keywords: 'full stack developer' },
            { location: 'Los Angeles, CA', keywords: 'ux designer' },
            { location: 'Chicago, IL', keywords: 'business analyst' },
            { location: 'Boston, MA', keywords: 'machine learning engineer' },
            { location: 'Remote', keywords: 'remote developer' }
        ];
        
        this.crawler = null;
        this.collectedJobs = [];
        this.processedPages = 0;
        this.errors = [];
    }

    /**
     * Initialize the crawler with anti-detection measures
     */
    async initialize() {
        console.log('🚀 Initializing Indeed UI Navigation Scraper...');
        
        this.crawler = new PlaywrightCrawler({
            headless: this.options.headless,
            launchContext: {
                launchOptions: {
                    // Anti-detection browser arguments
                    args: [
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=VizDisplayCompositor',
                        '--no-first-run',
                        '--no-default-browser-check'
                    ]
                }
            },
            maxConcurrency: this.options.maxConcurrency,
            requestHandlerTimeoutSecs: 120,
            
            requestHandler: async ({ page, request, log }) => {
                await this.handlePageRequest(page, request, log);
            },
            
            failedRequestHandler: async ({ request, log }) => {
                await this.handleFailedRequest(request, log);
            }
        });
        
        console.log('✅ Indeed UI scraper initialized');
    }

    /**
     * Main scraping orchestration method
     */
    async scrapeJobs(searchParams = {}) {
        const {
            maxPages = 10,
            maxJobsPerRegion = 1000,
            startFromRegion = 0
        } = searchParams;
        
        console.log(`🎯 Starting Indeed UI scraping: ${this.searchRegions.length} regions, max ${maxPages} pages each`);
        
        try {
            await this.initialize();
            
            // Process each geographic region
            for (let i = startFromRegion; i < this.searchRegions.length; i++) {
                const region = this.searchRegions[i];
                console.log(`\n📍 Processing region ${i + 1}/${this.searchRegions.length}: ${region.location}`);
                
                try {
                    const regionJobs = await this.scrapeRegion(region, maxPages, maxJobsPerRegion);
                    this.collectedJobs.push(...regionJobs);
                    
                    console.log(`✅ Region complete: ${regionJobs.length} jobs collected`);
                    
                    // Anti-detection delay between regions
                    await this.randomDelay(3000, 7000);
                    
                } catch (error) {
                    console.log(`❌ Region ${region.location} failed: ${error.message}`);
                    this.errors.push({
                        region: region.location,
                        error: error.message,
                        timestamp: new Date().toISOString()
                    });
                }
            }
            
            return this.getScrapingResults();
            
        } catch (error) {
            console.log(`❌ Indeed scraping failed: ${error.message}`);
            throw error;
        } finally {
            if (this.crawler) {
                await this.crawler.teardown();
            }
        }
    }

    /**
     * Scrape jobs from a specific geographic region
     */
    async scrapeRegion(region, maxPages, maxJobsPerRegion) {
        const regionJobs = [];
        let currentPage = 0;
        
        // Start with Indeed search page
        const searchUrl = 'https://www.indeed.com/';
        await this.crawler.addRequests([{ 
            url: searchUrl,
            userData: { 
                action: 'search_setup',
                region: region,
                maxPages: maxPages,
                maxJobsPerRegion: maxJobsPerRegion
            }
        }]);
        
        await this.crawler.run();
        
        return this.collectedJobs.filter(job => 
            job.searchRegion === region.location
        );
    }

    /**
     * Handle individual page requests
     */
    async handlePageRequest(page, request, log) {
        const { action, region, currentPage = 0, maxPages, maxJobsPerRegion } = request.userData || {};
        
        log.info(`Processing: ${action} for ${region?.location || 'unknown'}`);
        
        try {
            // Apply anti-detection measures
            await this.applyAntiDetectionMeasures(page);
            
            switch (action) {
                case 'search_setup':
                    await this.performInitialSearch(page, region, maxPages, maxJobsPerRegion);
                    break;
                
                case 'extract_jobs':
                    await this.extractJobsFromPage(page, region, currentPage, maxPages, maxJobsPerRegion);
                    break;
                
                default:
                    log.warning(`Unknown action: ${action}`);
            }
            
        } catch (error) {
            log.error(`Page processing failed: ${error.message}`);
            
            // Check for common blocking scenarios
            if (await this.detectBlocking(page)) {
                throw new Error('Indeed access blocked - anti-bot detection triggered');
            }
            
            throw error;
        }
    }

    /**
     * Apply comprehensive anti-detection measures
     */
    async applyAntiDetectionMeasures(page) {
        // Set random user agent
        const userAgent = this.userAgents[Math.floor(Math.random() * this.userAgents.length)];
        await page.setUserAgent(userAgent);
        
        // Set realistic viewport
        const viewports = [
            { width: 1920, height: 1080 },
            { width: 1366, height: 768 },
            { width: 1440, height: 900 },
            { width: 1280, height: 720 }
        ];
        const viewport = viewports[Math.floor(Math.random() * viewports.length)];
        await page.setViewportSize(viewport);
        
        // Remove automation indicators
        await page.addInitScript(() => {
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override plugins length
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Override chrome property
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Override permission query
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Cypress.config('isInteractive') ? 'granted' : 'default' }) :
                    originalQuery(parameters)
            );
        });
        
        // Set realistic headers
        await page.setExtraHTTPHeaders({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        });
    }

    /**
     * Perform initial job search with human-like behavior
     */
    async performInitialSearch(page, region, maxPages, maxJobsPerRegion) {
        console.log(`🔍 Setting up search for: ${region.keywords} in ${region.location}`);
        
        // Wait for page load with timeout
        await page.waitForLoadState('networkidle', { timeout: 30000 });
        
        // Human-like delay before interaction
        await this.randomDelay(1000, 3000);
        
        // Find and interact with search form
        const searchForm = await this.findElementWithFallbacks(page, [
            this.selectors.searchForm
        ]);
        
        if (!searchForm) {
            throw new Error('Could not locate Indeed search form');
        }
        
        // Fill keywords field
        const keywordsInput = await this.findElementWithFallbacks(page, [
            this.selectors.keywordsInput
        ]);
        
        if (keywordsInput) {
            await this.humanLikeTyping(keywordsInput, region.keywords);
            await this.randomDelay(500, 1500);
        }
        
        // Fill location field
        const locationInput = await this.findElementWithFallbacks(page, [
            this.selectors.locationInput
        ]);
        
        if (locationInput) {
            // Clear existing location text
            await locationInput.selectText();
            await this.humanLikeTyping(locationInput, region.location);
            await this.randomDelay(500, 1500);
        }
        
        // Submit search form
        const searchButton = await this.findElementWithFallbacks(page, [
            this.selectors.searchButton
        ]);
        
        if (searchButton) {
            await this.randomDelay(500, 1500);
            await searchButton.click();
            console.log('✅ Search submitted');
        } else {
            // Alternative: submit form directly
            await searchForm.press('Enter');
            console.log('✅ Search submitted via Enter key');
        }
        
        // Wait for results page
        await page.waitForLoadState('networkidle', { timeout: 30000 });
        
        // Check for successful search results
        const hasResults = await this.waitForJobResults(page);
        
        if (!hasResults) {
            throw new Error('No job results found after search submission');
        }
        
        // Start extracting jobs from first page
        await this.crawler.addRequests([{
            url: page.url(),
            userData: {
                action: 'extract_jobs',
                region: region,
                currentPage: 0,
                maxPages: maxPages,
                maxJobsPerRegion: maxJobsPerRegion
            }
        }]);
    }

    /**
     * Extract jobs from current results page
     */
    async extractJobsFromPage(page, region, currentPage, maxPages, maxJobsPerRegion) {
        console.log(`📄 Extracting jobs from page ${currentPage + 1}/${maxPages}`);
        
        // Wait for job cards to load
        await this.waitForJobResults(page);
        
        // Extract job data from all cards on page
        const jobCards = await page.locator(this.selectors.jobCards).all();
        const altJobCards = await page.locator(this.selectors.altJobCards).all();
        const allCards = [...jobCards, ...altJobCards];
        
        console.log(`🔍 Found ${allCards.length} job cards on page`);
        
        for (const card of allCards) {
            try {
                const jobData = await this.extractJobDataFromCard(card, region);
                
                if (jobData && this.validateJobData(jobData)) {
                    this.collectedJobs.push(jobData);
                }
                
                // Prevent memory buildup with large job collections
                if (this.collectedJobs.length >= maxJobsPerRegion) {
                    console.log(`🎯 Region job limit reached: ${maxJobsPerRegion} jobs`);
                    return;
                }
                
            } catch (error) {
                console.log(`⚠️ Failed to extract job data: ${error.message}`);
            }
        }
        
        this.processedPages++;
        console.log(`✅ Page ${currentPage + 1} complete: ${allCards.length} jobs processed`);
        
        // Check for next page if within limits
        if (currentPage + 1 < maxPages && this.collectedJobs.length < maxJobsPerRegion) {
            await this.navigateToNextPage(page, region, currentPage + 1, maxPages, maxJobsPerRegion);
        }
    }

    /**
     * Extract structured job data from a job card element
     */
    async extractJobDataFromCard(card, region) {
        const getTextContent = async (selectors) => {
            for (const selector of Array.isArray(selectors) ? selectors : [selectors]) {
                try {
                    const element = card.locator(selector).first();
                    const text = await element.textContent({ timeout: 2000 });
                    if (text && text.trim()) {
                        return text.trim();
                    }
                } catch (error) {
                    // Continue to next selector
                }
            }
            return null;
        };
        
        const getUrl = async (selectors) => {
            for (const selector of Array.isArray(selectors) ? selectors : [selectors]) {
                try {
                    const element = card.locator(selector).first();
                    const href = await element.getAttribute('href', { timeout: 2000 });
                    if (href) {
                        return href.startsWith('http') ? href : `https://www.indeed.com${href}`;
                    }
                } catch (error) {
                    // Continue to next selector
                }
            }
            return null;
        };
        
        try {
            const jobData = {
                title: await getTextContent([this.selectors.jobTitle, this.selectors.altJobTitle]),
                company: await getTextContent([this.selectors.companyName, this.selectors.altCompanyName]),
                location: await getTextContent([this.selectors.location, this.selectors.altLocation]),
                salary: await getTextContent([this.selectors.salary]),
                summary: await getTextContent([this.selectors.summary]),
                url: await getUrl([this.selectors.jobTitle, this.selectors.altJobTitle]),
                
                // Metadata
                source: 'indeed_ui',
                searchRegion: region.location,
                searchKeywords: region.keywords,
                extractedAt: new Date().toISOString(),
                pageNumber: this.processedPages + 1
            };
            
            // Generate unique job ID
            if (jobData.url) {
                jobData.jobId = `indeed_${this.generateJobId(jobData.url)}`;
            } else if (jobData.title && jobData.company) {
                jobData.jobId = `indeed_${this.generateJobId(jobData.title + jobData.company)}`;
            }
            
            return jobData;
            
        } catch (error) {
            console.log(`⚠️ Error extracting job data: ${error.message}`);
            return null;
        }
    }

    /**
     * Navigate to next page of results
     */
    async navigateToNextPage(page, region, nextPageNumber, maxPages, maxJobsPerRegion) {
        console.log(`➡️ Navigating to page ${nextPageNumber + 1}`);
        
        try {
            // Find next page link
            const nextPageLink = await this.findElementWithFallbacks(page, [
                this.selectors.nextPage
            ]);
            
            if (!nextPageLink) {
                console.log('ℹ️ No next page link found - end of results');
                return;
            }
            
            // Human-like delay before clicking
            await this.randomDelay(1000, 3000);
            
            // Click next page
            await nextPageLink.click();
            
            // Wait for page load
            await page.waitForLoadState('networkidle', { timeout: 30000 });
            
            // Verify we successfully navigated
            const hasResults = await this.waitForJobResults(page);
            
            if (!hasResults) {
                console.log('⚠️ Next page navigation failed - no results found');
                return;
            }
            
            // Add request to process next page
            await this.crawler.addRequests([{
                url: page.url(),
                userData: {
                    action: 'extract_jobs',
                    region: region,
                    currentPage: nextPageNumber,
                    maxPages: maxPages,
                    maxJobsPerRegion: maxJobsPerRegion
                }
            }]);
            
        } catch (error) {
            console.log(`❌ Next page navigation failed: ${error.message}`);
        }
    }

    /**
     * Wait for job results to load on page
     */
    async waitForJobResults(page, timeout = 15000) {
        try {
            await page.waitForSelector(this.selectors.jobCards, { timeout });
            return true;
        } catch (error) {
            // Try alternative selectors
            try {
                await page.waitForSelector(this.selectors.altJobCards, { timeout: 5000 });
                return true;
            } catch (altError) {
                console.log('⚠️ No job results found on page');
                return false;
            }
        }
    }

    /**
     * Find element using multiple fallback selectors
     */
    async findElementWithFallbacks(page, selectors) {
        for (const selector of selectors) {
            try {
                const element = page.locator(selector).first();
                await element.waitFor({ timeout: 3000 });
                return element;
            } catch (error) {
                // Continue to next selector
            }
        }
        return null;
    }

    /**
     * Human-like typing with realistic delays
     */
    async humanLikeTyping(element, text) {
        await element.clear();
        
        for (const char of text) {
            await element.type(char);
            // Random delay between characters (50-150ms)
            await this.randomDelay(50, 150);
        }
    }

    /**
     * Random delay with specified range
     */
    async randomDelay(min, max) {
        const delay = Math.random() * (max - min) + min;
        await new Promise(resolve => setTimeout(resolve, delay));
    }

    /**
     * Detect blocking or anti-bot measures
     */
    async detectBlocking(page) {
        try {
            // Check for common blocking indicators
            const blockingSelectors = [
                this.selectors.captcha,
                this.selectors.blocked
            ];
            
            for (const selector of blockingSelectors) {
                const element = await page.locator(selector).first();
                if (await element.isVisible({ timeout: 1000 })) {
                    return true;
                }
            }
            
            // Check page title for blocking messages
            const title = await page.title();
            const blockingTitles = ['Just a moment', 'Access denied', 'Blocked', 'Captcha'];
            
            return blockingTitles.some(blockTitle => 
                title.toLowerCase().includes(blockTitle.toLowerCase())
            );
            
        } catch (error) {
            return false;
        }
    }

    /**
     * Validate extracted job data quality
     */
    validateJobData(jobData) {
        const required = ['title', 'company'];
        const hasRequired = required.every(field => 
            jobData[field] && jobData[field].trim().length > 0
        );
        
        const hasUrl = jobData.url && jobData.url.includes('indeed.com');
        const hasLocation = jobData.location && jobData.location.trim().length > 0;
        
        return hasRequired && (hasUrl || hasLocation);
    }

    /**
     * Generate unique job ID from string
     */
    generateJobId(input) {
        let hash = 0;
        for (let i = 0; i < input.length; i++) {
            const char = input.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash).toString(16);
    }

    /**
     * Handle failed requests with retry logic
     */
    async handleFailedRequest(request, log) {
        const { retryCount = 0 } = request.userData || {};
        
        if (retryCount < 3) {
            log.info(`Retrying failed request (attempt ${retryCount + 1}): ${request.url}`);
            
            // Add delay before retry
            await this.randomDelay(2000, 5000);
            
            await this.crawler.addRequests([{
                ...request,
                userData: {
                    ...request.userData,
                    retryCount: retryCount + 1
                }
            }]);
        } else {
            log.error(`Request failed after 3 retries: ${request.url}`);
            this.errors.push({
                url: request.url,
                error: 'Max retries exceeded',
                timestamp: new Date().toISOString()
            });
        }
    }

    /**
     * Get comprehensive scraping results
     */
    getScrapingResults() {
        const uniqueJobs = this.deduplicateJobs(this.collectedJobs);
        
        return {
            summary: {
                totalJobsCollected: this.collectedJobs.length,
                uniqueJobsAfterDeduplication: uniqueJobs.length,
                pagesProcessed: this.processedPages,
                regionsProcessed: new Set(this.collectedJobs.map(job => job.searchRegion)).size,
                errorsEncountered: this.errors.length,
                scrapingDuration: 'Calculated in wrapper',
                averageJobsPerPage: Math.round(this.collectedJobs.length / this.processedPages)
            },
            jobs: uniqueJobs,
            errors: this.errors,
            metadata: {
                scraper: 'indeed_ui_navigation',
                scrapingMethod: 'Browser MCP automation',
                antiDetectionMeasures: 'Enabled',
                timestamp: new Date().toISOString()
            }
        };
    }

    /**
     * Remove duplicate jobs based on URL and title+company combination
     */
    deduplicateJobs(jobs) {
        const seen = new Set();
        const uniqueJobs = [];
        
        for (const job of jobs) {
            let identifier;
            
            if (job.url) {
                identifier = job.url;
            } else if (job.title && job.company) {
                identifier = `${job.title.toLowerCase()}_${job.company.toLowerCase()}`;
            } else {
                continue; // Skip jobs without proper identification
            }
            
            if (!seen.has(identifier)) {
                seen.add(identifier);
                uniqueJobs.push(job);
            }
        }
        
        return uniqueJobs;
    }
}

// Export for integration with existing scraper infrastructure
export { IndeedUINavigationScraper };

// Usage example for testing
if (import.meta.main) {
    const scraper = new IndeedUINavigationScraper({
        maxConcurrency: 1,
        headless: false
    });
    
    const results = await scraper.scrapeJobs({
        maxPages: 3,
        maxJobsPerRegion: 500,
        startFromRegion: 0
    });
    
    console.log('🎯 Indeed UI Scraping Complete!');
    console.log(`📊 Results: ${results.summary.uniqueJobsAfterDeduplication} unique jobs`);
    console.log(`📄 Pages: ${results.summary.pagesProcessed} processed`);
    console.log(`🌍 Regions: ${results.summary.regionsProcessed} covered`);
    
    if (results.errors.length > 0) {
        console.log(`⚠️ Errors: ${results.errors.length} encountered`);
    }
}