import apiClient from './api';
import type {
  ApiResponse,
  DashboardStats,
  ActivityItem,
  Server
} from '@/lib/types';

class DashboardService {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<ApiResponse<DashboardStats>> {
    return apiClient.get<DashboardStats>('/dashboard/stats');
  }

  /**
   * Get recent activity
   */
  async getActivity(limit: number = 10): Promise<ApiResponse<ActivityItem[]>> {
    return apiClient.get<ActivityItem[]>(`/dashboard/activity?limit=${limit}`);
  }

  /**
   * Get user's servers
   */
  async getServers(): Promise<ApiResponse<Server[]>> {
    return apiClient.get<Server[]>('/dashboard/servers');
  }

  /**
   * Get upcoming events
   */
  async getUpcomingEvents(limit: number = 5): Promise<ApiResponse<any[]>> {
    return apiClient.get<any[]>(`/dashboard/events?limit=${limit}`);
  }

  /**
   * Get quick actions available to user
   */
  async getQuickActions(): Promise<ApiResponse<any[]>> {
    return apiClient.get<any[]>('/dashboard/quick-actions');
  }

  /**
   * Create a new server
   */
  async createServer(serverData: { name: string; icon?: string }): Promise<ApiResponse<Server>> {
    return apiClient.post<Server>('/dashboard/servers', serverData);
  }

  /**
   * Delete a server
   */
  async deleteServer(serverId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/dashboard/servers/${serverId}`);
  }

  /**
   * Update server settings
   */
  async updateServer(serverId: string, data: Partial<Server>): Promise<ApiResponse<Server>> {
    return apiClient.put<Server>(`/dashboard/servers/${serverId}`, data);
  }
}

export const dashboardService = new DashboardService();
export default dashboardService;
