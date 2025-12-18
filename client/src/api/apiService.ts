import { API_CONFIG } from './config';

export interface ProductMetric {
    product_name: string;
    sales_count: number;
    total_revenue: number;
    total_margin: number;
    refund_rate?: number;
}

export interface FunnelSteps {
    sessions: number;
    products: number;
    cart: number;
    shipping: number;
    billing: number;
    purchase: number;
}

export interface DashboardData {
    traffic: any;
    conversion: {
        overall_conversion_rate: number;
        total_conversions: number;
        conversion_by_channel: Record<string, number>;
        conversion_by_device: Record<string, number>;
        funnel_steps: FunnelSteps;
    };
    revenue: any;
    quality: any;
    products: ProductMetric[];
}

class ApiService {
    private baseURL: string;

    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
    }

    async getDashboardData(timeRange: string = 'Month'): Promise<DashboardData> {
        try {
            const response = await fetch(`${this.baseURL}/api/dashboard?range=${timeRange}`);
            if (!response.ok) {
                // If backend is down or 500, we might want to return null or throw
                // But let's assume valid JSON error if expected
                const text = await response.text();
                try {
                    const json = JSON.parse(text);
                    throw new Error(json.detail || `HTTP error! status: ${response.status}`);
                } catch (e) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            }
            return await response.json();
        } catch (error) {
            console.error("Failed to fetch dashboard data:", error);
            throw error;
        }
    }

    async getQualityReport(): Promise<any> {
        try {
            const response = await fetch(`${this.baseURL}/api/quality`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Failed to fetch quality report:", error);
            throw error;
        }
    }

    async sendChat(question: string): Promise<any> {
        try {
            const response = await fetch(`${this.baseURL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question }),
            });
            if (!response.ok) throw new Error('Chat failed');
            return await response.json();
        } catch (error) {
            console.error("Chat error:", error);
            throw error;
        }
    }

    async getInsights(range: string): Promise<any> {
        try {
            const response = await fetch(`${this.baseURL}/api/insights?range=${range}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Failed to fetch insights:", error);
            throw error;
        }
    }
}

export const apiService = new ApiService();
