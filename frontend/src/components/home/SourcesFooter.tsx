const SOURCES = [
  {
    label: "UPI AutoPay approval rate decline (50% → 30%)",
    org: "Moneycontrol",
    url: "https://www.moneycontrol.com/news/business/startup/why-merchants-prefer-upi-autopay-despite-a-lower-success-rate-than-cards-13762634.html",
  },
  {
    label: "~20% of subsequent debits fail on balance/bank/mandate issues",
    org: "Razorpay Engineering Blog",
    url: "https://razorpay.com/blog/upi-autopay-with-intelligent-revenue-protect/",
  },
  {
    label: "NPCI: 1 initial attempt + 3 retries, non-peak execution windows",
    org: "Economic Times / ETBFSI",
    url: "https://economictimes.indiatimes.com/wealth/save/big-changes-to-upi-from-august-1-daily-limits-api-rules-and-penalties-introduced/fixed-time-windows-for-auto-debits-mandate-execution-limit/slideshow/123118019.cms",
  },
  {
    label: "24-hour pre-debit notification requirement",
    org: "RBI e-mandate framework",
    url: "https://docs.stripe.com/india-recurring-payments",
  },
  {
    label: "Failure rates reaching up to 90% in some cohorts",
    org: "Livemint",
    url: "https://www.livemint.com/companies/start-ups/upi-autopay-failures-recurring-payments-india-11759999218161.html",
  },
];

export function SourcesFooter() {
  return (
    <div className="grid gap-3 text-xs text-text-secondary sm:grid-cols-2">
      {SOURCES.map((s) => (
        <a
          key={s.url}
          href={s.url}
          target="_blank"
          rel="noreferrer"
          className="link-underline flex items-start gap-2 text-text-secondary hover:text-ai-400"
        >
          <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-ai-400" />
          <span>
            {s.label} <span className="text-text-muted">— {s.org}</span>
          </span>
        </a>
      ))}
    </div>
  );
}
