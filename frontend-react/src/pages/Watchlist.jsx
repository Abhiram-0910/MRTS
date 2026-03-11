import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Star, Film, X, AlertCircle } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

const Watchlist = () => {
    const { userId } = useAppContext();
    const [stats, setStats] = useState({ totalRated: 0, watchlistSize: 0 });
    const [watchlist, setWatchlist] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isError, setIsError] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            setIsLoading(true);
            setIsError(false);
            try {
                const [statsRes, watchlistRes] = await Promise.all([
                    axios.get(`${API_BASE}/api/user_stats/${userId}`),
                    axios.get(`${API_BASE}/api/watchlist/${userId}`)
                ]);

                setStats({
                    totalRated: (statsRes.data.movies_liked || 0) + (statsRes.data.tv_shows_liked || 0) + (statsRes.data.movies_disliked || 0),
                    watchlistSize: statsRes.data.watchlist_size || 0,
                });

                // watchlist endpoint returns { watchlist: [...], count: N }
                setWatchlist(watchlistRes.data.watchlist || []);
            } catch (error) {
                console.error('Watchlist fetch error:', error);
                setIsError(true);
                toast.error('Failed to load watchlist data.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, [userId]);

    const removeFromWatchlist = async (tmdbId, title) => {
        try {
            await axios.post(`${API_BASE}/api/watchlist`, {
                user_id: userId,
                tmdb_id: tmdbId,
                action: 'remove',
            });
            setWatchlist((prev) => prev.filter((item) => item.id !== tmdbId));
            setStats((prev) => ({ ...prev, watchlistSize: Math.max(0, prev.watchlistSize - 1) }));
            toast.success(`Removed ${title} from Watchlist`);
        } catch (error) {
            toast.error('Failed to remove item.');
        }
    };

    if (isError) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center py-16 px-4 bg-slate-900/30 rounded-2xl border border-dashed border-slate-700 mx-8 mt-12">
                <AlertCircle size={48} className="text-red-500 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">System Error</h3>
                <p className="text-slate-400">Failed to load the archive. Please try again.</p>
            </div>
        );
    }

    return (
        <div className="w-full flex-1 flex flex-col">
            {/* Stats Row */}
            <div className="flex flex-wrap gap-4 px-8 pb-8 mt-8">
                {isLoading ? (
                    <div className="flex min-w-[240px] flex-1 h-[120px] rounded-xl bg-slate-800/50 animate-pulse border border-slate-700"></div>
                ) : (
                    <>
                        <div className="flex min-w-[240px] flex-1 flex-col gap-3 rounded-xl p-6 border border-slate-800 bg-[#1a1f35] relative overflow-hidden group hover:border-blue-500/50 transition-colors">
                            <div className="flex justify-between items-start z-10">
                                <p className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Movies Rated</p>
                                <Star className="text-blue-500" size={20} />
                            </div>
                            <div className="flex items-baseline gap-3 z-10 mt-2">
                                <p className="text-slate-100 tracking-tight text-4xl font-bold leading-none">{stats.totalRated}</p>
                            </div>
                        </div>
                        <div className="flex min-w-[240px] flex-1 flex-col gap-3 rounded-xl p-6 border border-slate-800 bg-[#1a1f35] relative overflow-hidden group hover:border-purple-500/50 transition-colors">
                            <div className="flex justify-between items-start z-10">
                                <p className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Watchlist Size</p>
                                <Film className="text-purple-500" size={20} />
                            </div>
                            <div className="flex items-baseline gap-3 z-10 mt-2">
                                <p className="text-slate-100 tracking-tight text-4xl font-bold leading-none">{stats.watchlistSize}</p>
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* Main Content Area */}
            {isLoading ? (
                <div className="px-8 pb-4">
                    <div className="h-4 w-48 bg-slate-800/50 rounded mb-4 animate-pulse"></div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-0 border border-slate-800 rounded-xl overflow-hidden bg-[#1a1f35]">
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className="aspect-[2/3] bg-slate-800/50 animate-pulse border-r border-b border-slate-700/50"></div>
                        ))}
                    </div>
                </div>
            ) : watchlist.length === 0 ? (
                <section className="flex-1 flex flex-col items-center justify-center py-16 px-4 bg-slate-900/30 rounded-2xl border border-dashed border-slate-700 min-h-[400px] mx-8">
                    <div className="flex flex-col items-center max-w-md text-center gap-6">
                        <div className="relative size-32 mb-2">
                            <div className="absolute inset-0 bg-blue-500/10 rounded-full blur-2xl"></div>
                            <div className="relative bg-slate-800 size-full rounded-full flex items-center justify-center shadow-lg border border-slate-700">
                                <Film className="text-6xl text-blue-500" size={48} />
                            </div>
                        </div>
                        <div className="flex flex-col gap-3">
                            <h3 className="text-white text-2xl font-bold">Your watchlist is waiting for its first star</h3>
                            <p className="text-slate-400 text-base">Save movies you want to see later. Build your ultimate cinematic queue.</p>
                        </div>
                        <Link to="/" className="mt-4 flex items-center justify-center gap-2 rounded-full h-12 px-8 bg-blue-600 hover:bg-blue-500 text-white font-bold transition-all shadow-lg">
                            Discover Movies
                        </Link>
                    </div>
                </section>
            ) : (
                <>
                    <div className="px-8 pb-4">
                        <h3 className="text-slate-500 text-xs font-bold tracking-[0.2em] uppercase border-b border-slate-800 pb-4">Y O U R   A R C H I V E</h3>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-0 mx-8 border border-slate-800 rounded-xl overflow-hidden bg-[#1a1f35]">
                        {watchlist.map((item) => {
                            const poster = item.poster_path || 'https://via.placeholder.com/300x450/1e293b/94a3b8?text=No+Poster';
                            return (
                                <div key={item.id} className="relative group aspect-[2/3] border-r border-b border-slate-800 bg-slate-900">
                                    <img src={poster} alt={item.title} className="w-full h-full object-cover" />
                                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center flex-col gap-2 p-4 text-center">
                                        <h4 className="text-white font-bold text-sm leading-tight mb-2 drop-shadow-md">{item.title}</h4>
                                        <button
                                            onClick={() => removeFromWatchlist(item.id, item.title)}
                                            className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white hover:bg-red-500 transition-colors shadow-lg"
                                            title="Remove from Watchlist"
                                        >
                                            <X size={20} />
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </>
            )}
        </div>
    );
};

export default Watchlist;
