const { useEffect, useMemo, useState } = React;

const AREAS = ['Terminal A', 'Platform 2', 'North Gate', 'Bus Bay', 'NSCR Wing'];

function SearchIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </svg>
  );
}

function SettingsIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M12 3l1.2 2.5 2.8.4-2 2 .5 2.9-2.5-1.3-2.5 1.3.5-2.9-2-2 2.8-.4L12 3z" />
      <circle cx="12" cy="14" r="3.2" />
    </svg>
  );
}

function HomeIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M3 11.5L12 4l9 7.5" />
      <path d="M5.5 10.5V20h13V10.5" />
    </svg>
  );
}

function CameraIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <rect x="3" y="7" width="14" height="10" rx="3" />
      <path d="M17 10l4-2v8l-4-2" />
    </svg>
  );
}

function ChartIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M4 19h16" />
      <path d="M7 16V9" />
      <path d="M12 16V5" />
      <path d="M17 16v-4" />
    </svg>
  );
}

function GearIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <circle cx="12" cy="12" r="3.2" />
      <path d="M19.4 15a1 1 0 0 0 .2 1.1l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1 1 0 0 0-1.1-.2 1 1 0 0 0-.6.9V20a2 2 0 1 1-4 0v-.2a1 1 0 0 0-.6-.9 1 1 0 0 0-1.1.2l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1 1 0 0 0 .2-1.1 1 1 0 0 0-.9-.6H4a2 2 0 1 1 0-4h.2a1 1 0 0 0 .9-.6 1 1 0 0 0-.2-1.1l-.1-.1A2 2 0 1 1 7.6 4.8l.1.1a1 1 0 0 0 1.1.2h.1a1 1 0 0 0 .6-.9V4a2 2 0 1 1 4 0v.2a1 1 0 0 0 .6.9 1 1 0 0 0 1.1-.2l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1 1 0 0 0-.2 1.1v.1a1 1 0 0 0 .9.6h.2a2 2 0 1 1 0 4h-.2a1 1 0 0 0-.9.6z" />
    </svg>
  );
}

function IconButton({ children }) {
  return (
    <button className="flex h-11 w-11 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-700 shadow-sm transition hover:bg-gray-50">
      {children}
    </button>
  );
}

function getFallbackData() {
  const now = new Date();
  const timeLabel = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return {
    meta: {
      last_updated: now.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
      coverage: 'Metro Manila smart terminal pilot',
      sdgs: ['SDG 4', 'SDG 8', 'SDG 10', 'SDG 11']
    },
    headline: {
      terminal_name: 'North Gate Camera Feed',
      queue_length: 48,
      estimated_wait_minutes: 15,
      density_percent: 67,
      service_level: 'Moderate',
      confidence: 93,
      boarding_rate_per_min: 5
    },
    zones: [
      { name: 'Zone A', value: 72 },
      { name: 'Zone B', value: 58 },
      { name: 'Zone C', value: 64 },
      { name: 'Zone D', value: 49 }
    ],
    historical_queue: [
      { label: '7:00', value: 24 },
      { label: '7:30', value: 30 },
      { label: '8:00', value: 36 },
      { label: '8:30', value: 42 },
      { label: '9:00', value: 45 },
      { label: 'Now', value: 48 }
    ],
    predicted_wait: [
      { label: 'Now', value: 15 },
      { label: '+1h', value: 17 },
      { label: '+2h', value: 21 },
      { label: '+3h', value: 18 }
    ],
    alerts: [
      { level: 'high', title: 'North Gate', detail: 'Wait time spiked to 21 mins at 8:42 AM.', time: '8:42 AM', wait_minutes: 21 },
      { level: 'medium', title: 'Platform 2', detail: 'Short feeder delay created moderate crowding.', time: '8:16 AM', wait_minutes: 14 },
      { level: 'medium', title: 'Bus Bay', detail: 'Passenger loading slowed during turnover.', time: '7:58 AM', wait_minutes: 12 }
    ],
    terminals: [
      { name: 'Gate 1 Camera', project: 'Vision Sensor', status: 'Active', type: 'Camera' },
      { name: 'Passenger Counter', project: 'Queue Detection', status: 'Online', type: 'Counter' },
      { name: 'Dispatch Beacon', project: 'Fleet Sync', status: 'Healthy', type: 'Beacon' },
      { name: 'Platform Sensor', project: 'Crowd Density', status: 'Online', type: 'Sensor' }
    ],
    recommendations: []
  };
}

function pillClass(active) {
  return active
    ? 'bg-gray-900 text-white shadow-sm border-gray-900'
    : 'bg-white text-gray-600 border-gray-200';
}

function assetStatusClass(status) {
  if (status === 'Active' || status === 'Online' || status === 'Healthy') {
    return 'bg-emerald-50 text-emerald-700';
  }
  return 'bg-amber-50 text-amber-700';
}

function SimpleAreaChart({ values }) {
  const width = 280;
  const height = 88;
  const padding = 10;
  const max = Math.max(...values.map(item => item.value), 1);
  const min = Math.min(...values.map(item => item.value), 0);
  const range = Math.max(max - min, 1);

  const points = values.map((item, index) => {
    const x = padding + (index * (width - padding * 2)) / Math.max(values.length - 1, 1);
    const y = height - padding - ((item.value - min) / range) * (height - padding * 2);
    return { ...item, x, y };
  });

  const linePath = points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ');
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${height - padding} L ${points[0].x} ${height - padding} Z`;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-24 w-full">
      <path d={areaPath} fill="rgba(37,99,235,0.14)" />
      <path d={linePath} fill="none" stroke="#2563eb" strokeWidth="3" strokeLinecap="round" />
      {points.map(point => (
        <circle key={point.label} cx={point.x} cy={point.y} r="3.5" fill="#2563eb" />
      ))}
    </svg>
  );
}

function AreaPills({ activeArea, setActiveArea }) {
  return (
    <div className="no-scrollbar -mx-1 flex gap-2 overflow-x-auto px-1 pb-1">
      {AREAS.map(area => (
        <button
          key={area}
          onClick={() => setActiveArea(area)}
          className={`shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition ${pillClass(area === activeArea)}`}
        >
          {area}
        </button>
      ))}
    </div>
  );
}

function CameraFeedCard({ data }) {
  const timestamp = data.meta.last_updated;
  const wait = data.headline.estimated_wait_minutes;

  return (
    <div className="rounded-[28px] bg-white p-3 shadow-card">
      <div className="relative overflow-hidden rounded-[24px] bg-gradient-to-br from-slate-800 via-slate-700 to-slate-900 p-4 text-white shadow-inner">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.16),transparent_30%),linear-gradient(135deg,rgba(255,255,255,0.04),transparent_40%)]" />
        <div className="relative z-10 flex items-center justify-between text-[11px] font-medium tracking-wide">
          <div className="flex items-center gap-2 rounded-full bg-black/35 px-3 py-1.5 backdrop-blur">
            <span className="h-2.5 w-2.5 rounded-full bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.9)]" />
            <span>LIVE</span>
          </div>
          <div className="rounded-full bg-black/35 px-3 py-1.5 backdrop-blur">REC</div>
        </div>

        <div className="relative z-10 mt-4 rounded-[22px] border border-white/10 bg-black/20 p-4 backdrop-blur-sm">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.22em] text-white/70">Camera Feed</div>
              <h2 className="mt-2 text-xl font-semibold">{data.headline.terminal_name}</h2>
            </div>
            <div className="rounded-full bg-white/12 px-3 py-1 text-xs">{timestamp}</div>
          </div>

          <div className="mt-5 grid grid-cols-4 gap-2">
            {data.zones.map(zone => (
              <div key={zone.name} className="rounded-2xl bg-white/8 px-2 py-3 text-center backdrop-blur-sm">
                <div
                  className="mx-auto mb-2 w-full rounded-xl bg-gradient-to-t from-cyan-400/55 via-sky-300/70 to-white/90"
                  style={{ height: `${Math.max(32, zone.value)}px` }}
                />
                <div className="text-[10px] text-white/70">{zone.name}</div>
              </div>
            ))}
          </div>

          <div className="mt-5 flex items-end justify-between">
            <div>
              <div className="text-sm text-white/70">Queue detected</div>
              <div className="text-4xl font-bold">{data.headline.queue_length}</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-white/70">Confidence</div>
              <div className="text-2xl font-semibold">{data.headline.confidence}%</div>
            </div>
          </div>
        </div>

        <div className="absolute bottom-4 left-4 right-4 z-20">
          <div className="rounded-2xl bg-white px-4 py-3 text-gray-900 shadow-float">
            <div className="text-[11px] uppercase tracking-[0.22em] text-gray-500">Predictive AI</div>
            <div className="mt-1 text-lg font-semibold">Estimated Wait Time: {wait} mins</div>
          </div>
        </div>

        <div className="h-20" />
      </div>
    </div>
  );
}

function StatRow({ data }) {
  return (
    <div className="grid grid-cols-3 gap-3">
      <div className="rounded-2xl bg-white p-4 shadow-sm">
        <div className="text-xs uppercase tracking-[0.18em] text-gray-400">Queue</div>
        <div className="mt-2 text-2xl font-semibold text-gray-900">{data.headline.queue_length}</div>
      </div>
      <div className="rounded-2xl bg-white p-4 shadow-sm">
        <div className="text-xs uppercase tracking-[0.18em] text-gray-400">Boarding</div>
        <div className="mt-2 text-2xl font-semibold text-gray-900">{data.headline.boarding_rate_per_min}/m</div>
      </div>
      <div className="rounded-2xl bg-white p-4 shadow-sm">
        <div className="text-xs uppercase tracking-[0.18em] text-gray-400">Density</div>
        <div className="mt-2 text-2xl font-semibold text-gray-900">{data.headline.density_percent}%</div>
      </div>
    </div>
  );
}

function ForecastCard({ data }) {
  return (
    <div className="rounded-3xl bg-white p-5 shadow-card">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-gray-400">Predictive AI</div>
          <h3 className="mt-2 text-lg font-semibold text-gray-900">Wait Time Trend</h3>
        </div>
        <div className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600">Next 3 hours</div>
      </div>
      <div className="mt-4">
        <SimpleAreaChart values={data.predicted_wait} />
      </div>
      <div className="mt-2 grid grid-cols-4 gap-2">
        {data.predicted_wait.map(item => (
          <div key={item.label} className="rounded-2xl bg-gray-50 p-3 text-center">
            <div className="text-[11px] text-gray-500">{item.label}</div>
            <div className="mt-1 text-sm font-semibold text-gray-900">{item.value}m</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AlertCard({ item }) {
  return (
    <div className="w-[220px] shrink-0 rounded-3xl bg-white p-3 shadow-card">
      <div className="relative overflow-hidden rounded-[22px] bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900 p-4 text-white">
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),transparent)]" />
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <span className="rounded-full bg-white/15 px-2.5 py-1 text-[10px] uppercase tracking-wide">{item.title}</span>
            <span className="rounded-full bg-red-500 px-2.5 py-1 text-[10px] font-semibold">{item.wait_minutes}m</span>
          </div>
          <div className="mt-12 rounded-2xl bg-white/10 p-3 backdrop-blur-sm">
            <div className="text-xs text-white/70">Recent bottleneck</div>
            <div className="mt-1 text-sm font-semibold leading-5">{item.detail}</div>
          </div>
          <div className="mt-4 text-[11px] text-white/70">{item.time}</div>
        </div>
      </div>
    </div>
  );
}

function AssetCard({ asset }) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-gray-900">{asset.name}</div>
          <div className="mt-1 text-xs text-gray-500">{asset.project}</div>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-[11px] font-medium ${assetStatusClass(asset.status)}`}>
          {asset.status}
        </span>
      </div>
      <div className="mt-4 text-xs uppercase tracking-[0.18em] text-gray-400">{asset.type}</div>
    </div>
  );
}

function BottomNav() {
  const items = [
    { label: 'Home', icon: HomeIcon, active: true },
    { label: 'Cameras', icon: CameraIcon },
    { label: 'Analytics', icon: ChartIcon },
    { label: 'Settings', icon: GearIcon }
  ];

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-4 z-50 flex justify-center px-4">
      <div className="pointer-events-auto w-full max-w-sm rounded-full border border-gray-200 bg-white/95 px-3 py-2 shadow-app backdrop-blur">
        <div className="grid grid-cols-4">
          {items.map(item => {
            const Icon = item.icon;
            return (
              <button key={item.label} className="flex flex-col items-center gap-1 rounded-full py-2 text-xs text-gray-500">
                <div className={`flex h-9 w-9 items-center justify-center rounded-full ${item.active ? 'bg-gray-900 text-white' : 'text-gray-500'}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <span className={item.active ? 'font-medium text-gray-900' : ''}>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function App() {
  const [activeArea, setActiveArea] = useState('North Gate');
  const [data, setData] = useState(getFallbackData());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const loadData = async () => {
      try {
        const response = await fetch('/api/dashboard/prototype');
        if (!response.ok) throw new Error('Failed');
        const payload = await response.json();
        if (mounted) {
          setData({
            ...payload,
            alerts: (payload.alerts || []).map((item, index) => ({
              ...item,
              time: item.time || ['8:42 AM', '8:16 AM', '7:58 AM'][index] || payload.meta.last_updated,
              wait_minutes: item.wait_minutes || (payload.predicted_wait?.[Math.min(index + 1, (payload.predicted_wait || []).length - 1)]?.value ?? 15)
            })),
            terminals: (payload.terminals || []).map((item, index) => ({
              ...item,
              project: item.project || 'Transit Asset',
              type: item.type || ['Camera', 'Counter', 'Beacon', 'Sensor'][index % 4]
            }))
          });
          setLoading(false);
        }
      } catch (error) {
        if (mounted) setLoading(false);
      }
    };

    loadData();
    const timer = setInterval(loadData, 10000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  const subtitle = useMemo(() => {
    if (loading) return 'Syncing terminal feed...';
    return `${activeArea} • ${data.meta.coverage}`;
  }, [activeArea, data, loading]);

  return (
    <div className="min-h-screen bg-gray-100 px-3 py-4 sm:px-6 sm:py-8">
      <div className="mx-auto max-w-5xl">
        <div className="mx-auto max-w-md rounded-[36px] bg-gray-50 p-4 shadow-app sm:p-5">
          <header className="mb-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs uppercase tracking-[0.2em] text-gray-400">Smart Transit</div>
                <h1 className="mt-1 text-2xl font-bold text-gray-900">Transit Hub</h1>
              </div>
              <div className="flex items-center gap-2">
                <IconButton><SearchIcon className="h-5 w-5" /></IconButton>
                <IconButton><SettingsIcon className="h-5 w-5" /></IconButton>
              </div>
            </div>
            <p className="mt-3 text-sm text-gray-500">{subtitle}</p>
          </header>

          <section className="mb-5">
            <AreaPills activeArea={activeArea} setActiveArea={setActiveArea} />
          </section>

          <section className="mb-5">
            <CameraFeedCard data={data} />
          </section>

          <section className="mb-5">
            <StatRow data={data} />
          </section>

          <section className="mb-5">
            <ForecastCard data={data} />
          </section>

          <section className="mb-5">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <div className="text-xs uppercase tracking-[0.2em] text-gray-400">Recent Bottlenecks</div>
                <h2 className="mt-1 text-lg font-semibold text-gray-900">AI Queue Alerts</h2>
              </div>
              <button className="text-sm font-medium text-gray-500">View all</button>
            </div>
            <div className="no-scrollbar -mx-1 flex gap-3 overflow-x-auto px-1 pb-1">
              {data.alerts.map(item => (
                <AlertCard key={`${item.title}-${item.time}`} item={item} />
              ))}
            </div>
          </section>

          <section className="pb-24">
            <div className="mb-3">
              <div className="text-xs uppercase tracking-[0.2em] text-gray-400">Infrastructure</div>
              <h2 className="mt-1 text-lg font-semibold text-gray-900">Terminal Sensors</h2>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {data.terminals.map(asset => (
                <AssetCard key={asset.name} asset={asset} />
              ))}
            </div>

            <div className="mt-5 rounded-2xl bg-white p-4 text-sm text-gray-500 shadow-sm">
              Aligned with SDGs 4, 8, 10, and 11 through smarter wait-time visibility and more equitable transit access.
            </div>
          </section>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('dashboard-root')).render(<App />);
