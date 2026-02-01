import { Check, Zap, Star } from "lucide-react";

export default function PricingSection() {
  const plans = [
    {
      name: "Starter",
      description: "Perfect for small communities",
      price: 0,
      period: "free forever",
      features: [
        "1 Server Boost",
        "Basic Analytics",
        "5 Custom Commands",
        "Community Support",
        "Email Updates",
        "Standard Speed"
      ],
      cta: "Get Started",
      popular: false
    },
    {
      name: "Pro",
      description: "For growing communities",
      price: 9.99,
      period: "per month",
      features: [
        "10 Server Boosts",
        "Advanced Analytics",
        "Unlimited Commands",
        "Priority Support",
        "Real-time Notifications",
        "Fast Delivery",
        "Custom Roles",
        "Scheduled Tasks",
        "Bot Integration"
      ],
      cta: "Start Free Trial",
      popular: true
    },
    {
      name: "Enterprise",
      description: "For large organizations",
      price: 29.99,
      period: "per month",
      features: [
        "Unlimited Server Boosts",
        "Enterprise Analytics",
        "Everything in Pro",
        "Dedicated Support",
        "SLA Guarantee",
        "Custom Integrations",
        "White-label Options",
        "Advanced Security",
        "API Access",
        "Multi-server Management"
      ],
      cta: "Contact Sales",
      popular: false
    }
  ];

  return (
    <section id="pricing" className="py-24 bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-primary-50 rounded-full px-4 py-2 mb-6">
            <Zap className="h-4 w-4 text-primary-600" />
            <span className="text-sm font-semibold text-primary-900">Pricing</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Choose the perfect plan for your community. No hidden fees, cancel anytime.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative rounded-2xl p-8 transition-all duration-300 ${
                plan.popular
                  ? "bg-white border-2 border-primary-500 shadow-xl shadow-primary-500/10 scale-105"
                  : "bg-white border border-gray-200 hover:shadow-lg"
              }`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white text-sm font-semibold px-4 py-1.5 rounded-full flex items-center space-x-1">
                    <Star className="h-4 w-4" />
                    <span>Most Popular</span>
                  </div>
                </div>
              )}

              {/* Plan Info */}
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </h3>
                <p className="text-gray-600 mb-4">{plan.description}</p>
                <div className="flex items-baseline justify-center">
                  <span className="text-5xl font-bold text-gray-900">
                    {plan.price === 0 ? "Free" : `$${plan.price}`}
                  </span>
                  {plan.price > 0 && (
                    <span className="text-gray-600 ml-2">/{plan.period}</span>
                  )}
                </div>
              </div>

              {/* Features List */}
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center mt-0.5">
                      <Check className="h-3 w-3 text-green-600" />
                    </div>
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <button
                className={`w-full py-4 px-6 rounded-xl font-semibold transition-all duration-200 ${
                  plan.popular
                    ? "bg-gradient-to-r from-primary-600 to-primary-700 text-white hover:shadow-lg hover:shadow-primary-500/25"
                    : "bg-gray-100 text-gray-900 hover:bg-gray-200"
                }`}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>

        {/* Trust Badges */}
        <div className="mt-16 flex flex-wrap justify-center items-center gap-8 text-gray-500 text-sm">
          <div className="flex items-center space-x-2">
            <Check className="h-5 w-5 text-green-600" />
            <span>Cancel anytime</span>
          </div>
          <div className="flex items-center space-x-2">
            <Check className="h-5 w-5 text-green-600" />
            <span>14-day free trial</span>
          </div>
          <div className="flex items-center space-x-2">
            <Check className="h-5 w-5 text-green-600" />
            <span>No credit card required</span>
          </div>
        </div>
      </div>
    </section>
  );
}
