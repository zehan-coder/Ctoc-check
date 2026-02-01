import { Star, Quote } from "lucide-react";

export default function TestimonialsSection() {
  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Community Manager",
      server: "Tech Enthusiasts (50K+ members)",
      avatar: "SJ",
      rating: 5,
      content: "BoostSync has completely transformed how we manage our community. The analytics alone are worth the investment."
    },
    {
      name: "Michael Chen",
      role: "Server Owner",
      server: "Gaming Hub (100K+ members)",
      avatar: "MC",
      rating: 5,
      content: "The instant boost feature is incredible. We went from level 1 to level 3 in just two weeks. Highly recommend!"
    },
    {
      name: "Emily Rodriguez",
      role: "Discord Admin",
      server: "Creative Artists (25K+ members)",
      avatar: "ER",
      rating: 5,
      content: "Best platform for Discord server management. The support team is amazing and always ready to help."
    }
  ];

  const stats = [
    { value: "10K+", label: "Active Servers" },
    { value: "5M+", label: "Members Managed" },
    { value: "99.9%", label: "Uptime" },
    { value: "4.9/5", label: "User Rating" }
  ];

  return (
    <section id="testimonials" className="py-24 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-primary-50 rounded-full px-4 py-2 mb-6">
            <Quote className="h-4 w-4 text-primary-600" />
            <span className="text-sm font-semibold text-primary-900">Testimonials</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            Loved by Communities
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            See what server owners and community managers are saying about BoostSync
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent mb-2">
                {stat.value}
              </div>
              <div className="text-gray-600 font-medium">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-2xl p-8 hover:shadow-xl transition-shadow duration-300"
            >
              {/* Rating */}
              <div className="flex space-x-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star
                    key={i}
                    className="h-5 w-5 text-yellow-400 fill-yellow-400"
                  />
                ))}
              </div>

              {/* Quote */}
              <p className="text-gray-700 leading-relaxed mb-6">
                &quot;{testimonial.content}&quot;
              </p>

              {/* Author */}
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center text-white font-semibold">
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-semibold text-gray-900">
                    {testimonial.name}
                  </div>
                  <div className="text-sm text-gray-600">
                    {testimonial.role}
                  </div>
                  <div className="text-xs text-primary-600 font-medium">
                    {testimonial.server}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
