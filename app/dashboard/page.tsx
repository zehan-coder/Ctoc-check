import Link from "next/link";
import {
  Zap,
  Users,
  BarChart3,
  Settings,
  Bell,
  Search,
  Plus,
  TrendingUp,
  ArrowUpRight,
  Calendar,
  Clock
} from "lucide-react";

export default function DashboardPage() {
  const stats = [
    {
      label: "Total Members",
      value: "24,521",
      change: "+12.5%",
      trend: "up",
      icon: Users
    },
    {
      label: "Server Boosts",
      value: "15",
      change: "+3",
      trend: "up",
      icon: Zap
    },
    {
      label: "Active Now",
      value: "1,234",
      change: "+8.2%",
      trend: "up",
      icon: BarChart3
    },
    {
      label: "Messages (24h)",
      value: "8,456",
      change: "+15.3%",
      trend: "up",
      icon: TrendingUp
    }
  ];

  const recentActivity = [
    {
      type: "boost",
      message: "Server boosted to Level 3",
      time: "2 hours ago",
      icon: Zap
    },
    {
      type: "member",
      message: "125 new members joined",
      time: "5 hours ago",
      icon: Users
    },
    {
      type: "message",
      message: "Daily message goal reached",
      time: "8 hours ago",
      icon: BarChart3
    },
    {
      type: "alert",
      message: "Security alert: 3 suspicious logins",
      time: "12 hours ago",
      icon: Bell
    }
  ];

  const quickActions = [
    {
      label: "Add Server Boost",
      href: "/dashboard/boosts",
      icon: Zap,
      color: "from-primary-500 to-primary-600"
    },
    {
      label: "View Analytics",
      href: "/dashboard/analytics",
      icon: BarChart3,
      color: "from-purple-500 to-purple-600"
    },
    {
      label: "Manage Members",
      href: "/dashboard/members",
      icon: Users,
      color: "from-green-500 to-green-600"
    },
    {
      label: "Settings",
      href: "/dashboard/settings",
      icon: Settings,
      color: "from-gray-500 to-gray-600"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Search */}
          <div className="flex-1 flex items-center">
            <div className="max-w-md w-full">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
              <Bell className="h-5 w-5" />
            </button>
            <div className="h-8 w-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center text-white font-semibold text-sm">
              JD
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome back, John!</p>
          </div>
          <button className="flex items-center space-x-2 bg-gradient-to-r from-primary-600 to-primary-700 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all duration-200">
            <Plus className="h-5 w-5" />
            <span>Add Server</span>
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                  <stat.icon className="h-6 w-6 text-gray-600" />
                </div>
                {stat.trend === "up" && (
                  <div className="flex items-center text-green-600 text-sm font-medium">
                    <ArrowUpRight className="h-4 w-4 mr-1" />
                    {stat.change}
                  </div>
                )}
              </div>
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {stat.value}
              </div>
              <div className="text-sm text-gray-600">
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 gap-4">
                {quickActions.map((action, index) => (
                  <Link
                    key={index}
                    href={action.href}
                    className="group p-4 rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all duration-200"
                  >
                    <div className={`w-10 h-10 bg-gradient-to-br ${action.color} rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                      <action.icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="text-sm font-medium text-gray-900">
                      {action.label}
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
                <Link href="/dashboard/activity" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  View all
                </Link>
              </div>
              <div className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-start space-x-4 p-4 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      activity.type === 'boost' ? 'bg-yellow-100' :
                      activity.type === 'member' ? 'bg-green-100' :
                      activity.type === 'message' ? 'bg-blue-100' :
                      'bg-red-100'
                    }`}>
                      <activity.icon className={`h-5 w-5 ${
                        activity.type === 'boost' ? 'text-yellow-600' :
                        activity.type === 'member' ? 'text-green-600' :
                        activity.type === 'message' ? 'text-blue-600' :
                        'text-red-600'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-900 font-medium">{activity.message}</p>
                      <div className="flex items-center text-sm text-gray-500 mt-1">
                        <Clock className="h-4 w-4 mr-1" />
                        {activity.time}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Upcoming Events */}
        <div className="mt-8">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Upcoming Events</h2>
              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center">
                <Plus className="h-4 w-4 mr-1" />
                Add event
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <Calendar className="h-5 w-5 text-primary-600" />
                  <span className="text-sm font-medium text-gray-900">Community Meetup</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">Weekly community call</p>
                <div className="text-xs text-gray-500">Tomorrow at 7:00 PM</div>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <Calendar className="h-5 w-5 text-primary-600" />
                  <span className="text-sm font-medium text-gray-900">Gaming Tournament</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">Monthly gaming event</p>
                <div className="text-xs text-gray-500">Saturday at 3:00 PM</div>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <Calendar className="h-5 w-5 text-primary-600" />
                  <span className="text-sm font-medium text-gray-900">AMA Session</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">Ask Me Anything with admins</p>
                <div className="text-xs text-gray-500">Next Sunday at 5:00 PM</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
