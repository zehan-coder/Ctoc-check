// User types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// Dashboard types
export interface DashboardStats {
  totalMembers: number;
  serverBoosts: number;
  activeNow: number;
  messages24h: number;
  memberChange: string;
  boostChange: string;
  activeChange: string;
  messageChange: string;
}

export interface ActivityItem {
  id: string;
  type: 'boost' | 'member' | 'message' | 'alert';
  message: string;
  time: string;
}

export interface QuickAction {
  label: string;
  href: string;
  icon: string;
  color: string;
}

// Server types
export interface Server {
  id: string;
  name: string;
  icon?: string;
  memberCount: number;
  level: number;
  boosts: number;
  ownerId: string;
  createdAt: string;
}

export interface CreateServerRequest {
  name: string;
  icon?: string;
}

// Boost types
export interface BoostPackage {
  id: string;
  name: string;
  boosts: number;
  price: number;
  currency: string;
  features: string[];
  popular?: boolean;
}

export interface BoostPurchase {
  id: string;
  serverId: string;
  packageId: string;
  status: 'pending' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    totalPages?: number;
  };
}
