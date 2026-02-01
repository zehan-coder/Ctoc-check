import apiClient from './api';
import type {
  ApiResponse,
  BoostPackage,
  BoostPurchase
} from '@/lib/types';

class BoostService {
  /**
   * Get available boost packages
   */
  async getPackages(): Promise<ApiResponse<BoostPackage[]>> {
    return apiClient.get<BoostPackage[]>('/boosts/packages');
  }

  /**
   * Get package by ID
   */
  async getPackage(packageId: string): Promise<ApiResponse<BoostPackage>> {
    return apiClient.get<BoostPackage>(`/boosts/packages/${packageId}`);
  }

  /**
   * Purchase a boost package
   */
  async purchaseBoost(packageId: string, serverId: string): Promise<ApiResponse<BoostPurchase>> {
    return apiClient.post<BoostPurchase>('/boosts/purchase', {
      packageId,
      serverId,
    });
  }

  /**
   * Get boost purchase history
   */
  async getPurchases(limit: number = 20, offset: number = 0): Promise<ApiResponse<BoostPurchase[]>> {
    return apiClient.get<BoostPurchase[]>(`/boosts/purchases?limit=${limit}&offset=${offset}`);
  }

  /**
   * Get purchase details
   */
  async getPurchase(purchaseId: string): Promise<ApiResponse<BoostPurchase>> {
    return apiClient.get<BoostPurchase>(`/boosts/purchases/${purchaseId}`);
  }

  /**
   * Cancel a pending boost purchase
   */
  async cancelPurchase(purchaseId: string): Promise<ApiResponse<void>> {
    return apiClient.post<void>(`/boosts/purchases/${purchaseId}/cancel`, {});
  }

  /**
   * Get boost usage statistics
   */
  async getUsageStats(serverId: string): Promise<ApiResponse<any>> {
    return apiClient.get<any>(`/boosts/stats/${serverId}`);
  }
}

export const boostService = new BoostService();
export default boostService;
