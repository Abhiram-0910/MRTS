import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Star, Film, X, AlertCircle, Loader2 } from 'lucide-react';
import api from '../services/api';

const Watchlist = () => {
  const [stats, setStats]       = useState({ movies_liked: 0, movies_disliked: 0, watchlist_size: 0 });
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [isError, setError]     = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const [statsRes, listRes] = await Promise.all([
        api.get('/api/user_stats'),
        api.get('/api/watchlist'),
      ]);
      setStats(statsRes.data);
      setWatchlist(listRes.data.watchlist || []);
    } catch (err) {
      console.error('Watchlist fetch error:', err);
      setError(true);
      toast.error('Failed to load watchlist.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const removeItem = async (tmdbId, title) => {
    try {
      await api.post('/api/watchlist', { tmdb_id: tmdbId, action: 'remove' });
      setWatchlist((prev) => prev.filter((i) => i.id !== tmdbId));
      setStats((prev) => ({ ...prev, watchlist_size: Math.max(0, prev.watchlist_size - 1) }));
      toast.success(`Removed "${title}" from Watchlist`);
    } catch {
      toast.error('Failed to remove item.');
    }
  };

  if (isError) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center py-24 px-4 gap-4">
        <AlertCircle size={48} className="text-red-500" />
        <h3 className="text-xl font-bold text-white">Failed to load watchlist</h3>
        <button onClick={fetchData} className="text-blue-400 hover:text-blue-300 text-sm underline">
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">Your Archive</h1>

      {/* ── Stats ─────────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {[
          { label: 'Loved', value: stats.movies_liked,    color: 'text-rose-400',   border: 'hover:border-rose-500/40' },
          { label: 'Passed', value: stats.movies_disliked, color: 'text-slate-400', border: 'hover:border-slate-500/40' },
          { label: 'Watchlist', value: stats.watchlist_size, color: 'text-blue-400', border: 'hover:border-blue-500/40' },
        ].map(({ label, value, color, border }) => (
          <div key={label}
            className={`bg-slate-900/60 border border-slate-800 ${border} rounded-2xl p-6 transition-all`}
          >
            {loading ? (
              <div className="h-10 bg-slate-800 animate-pulse rounded" />
            ) : (
              <>
                <p className="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2">{label}</p>
                <p className={`text-4xl font-bold ${color}`}>{value}</p>
              </>
            )}
          </div>
        ))}
      </div>

      {/* ── Watchlist grid ────────────────────────────────────────────────── */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aspect-[2/3] bg-slate-800 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : watchlist.length === 0 ? (
        <section className="flex flex-col items-center justify-center py-24 border border-dashed border-slate-700 rounded-2xl gap-6">
          <div className="relative size-28">
            <div className="absolute inset-0 bg-blue-500/10 rounded-full blur-2xl" />
            <div className="relative size-full rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
              <Film size={44} className="text-blue-500" />
            </div>
          </div>
          <div className="text-center">
            <h3 className="text-white text-xl font-bold mb-2">Your watchlist is empty</h3>
            <p className="text-slate-400 text-sm">Save movies to watch later using the 🔖 button on any card.</p>
          </div>
          <Link to="/" className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-2.5 rounded-xl transition-all">
            Discover Movies
          </Link>
        </section>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          {watchlist.map((item) => (
            <div key={item.id} className="group relative aspect-[2/3] bg-slate-800 rounded-2xl overflow-hidden border border-slate-800 hover:border-slate-700 transition-all">
              {item.poster_path ? (
                <img src={item.poster_path} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Film size={36} className="text-slate-600" />
                </div>
              )}
              {/* Hover overlay */}
              <div className="absolute inset-0 bg-black/70 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-3 p-3 text-center">
                <p className="text-white font-semibold text-sm leading-tight line-clamp-3">{item.title}</p>
                {item.rating && (
                  <span className="flex items-center gap-1 text-amber-400 text-xs">
                    <Star size={10} fill="currentColor" /> {item.rating?.toFixed(1)}
                  </span>
                )}
                <button
                  onClick={() => removeItem(item.id, item.title)}
                  className="w-9 h-9 rounded-full bg-white/10 hover:bg-red-500 flex items-center justify-center text-white transition-colors"
                  title="Remove from Watchlist"
                >
                  <X size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Watchlist;
