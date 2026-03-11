import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { Search, CornerDownLeft, Star, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

const Home = () => {
    const { userId, language } = useAppContext();
    const [query, setQuery] = useState('');
    const [mediaType] = useState('All');
    const [minRating] = useState(6.0);
    const [genre] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [recommendations, setRecommendations] = useState([]);
    const [aiExplanation, setAiExplanation] = useState('');
    const [hasSearched, setHasSearched] = useState(false);
    const [isError, setIsError] = useState(false);
    const [expandedId, setExpandedId] = useState(null);

    const handleSearch = async (e) => {
        e?.preventDefault();
        if (!query.trim()) return;

        setIsLoading(true);
        setHasSearched(true);
        setIsError(false);
        setRecommendations([]);
        setAiExplanation('');

        try {
            const { data } = await axios.post(`${API_BASE}/api/recommend`, {
                query,
                user_id: userId,
                media_type: mediaType,
                min_rating: minRating,
                language_pref: language,
                genre: genre,
            });

            setRecommendations(data.movies || []);
            setAiExplanation(data.explanation || '');
            if (data.movies && data.movies.length === 0) {
                toast('No matches found. Try adjusting your search!', { icon: '🤔' });
            }
        } catch (error) {
            console.error('Search error:', error);
            if (error.response?.status === 429) {
                // Rate limit hit - show toast but don't crash UI
                const msg = error.response?.data?.detail || 'Too many requests. Please wait a moment.';
                toast.error(msg, { duration: 5000 });
            } else {
                // Hard failure
                setIsError(true);
                toast.error('Failed to get recommendations. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleRate = async (tmdbId, type, title) => {
        try {
            await axios.post(`${API_BASE}/api/rate`, {
                user_id: userId,
                tmdb_id: tmdbId,
                interaction_type: type,
            });
            if (type === 'like') {
                toast.success(`❤️ Loved ${title}!`);
            } else {
                toast(`👎 Passed on ${title}`);
            }
        } catch (error) {
            toast.error('Failed to save rating. Need to be logged in?');
        }
    };

    const addToWatchlist = async (tmdbId, title) => {
        try {
            await axios.post(`${API_BASE}/api/watchlist`, {
                user_id: userId,
                tmdb_id: tmdbId,
                action: 'add',
            });
            toast.success(`📋 Added ${title} to Watchlist!`);
        } catch (error) {
            toast.error('Failed to add to watchlist.');
        }
    };

    return (
        <div className="w-full flex-1 flex flex-col items-center">
            {/* Hero Search */}
            <div className="w-full flex justify-start mb-8 mt-12 px-8">
                <h1 className="text-slate-400 tracking-tighter text-[60px] font-black leading-none uppercase">MOVIE & TV SHOWS RECOMMENDING ENGINE.</h1>
            </div>
            <div className="w-full max-w-3xl px-8 flex flex-col items-start gap-4">
                <form onSubmit={handleSearch} className="w-full">
                    <div className="flex w-full items-stretch rounded-2xl h-16 border border-slate-800 bg-[#151a2e] overflow-hidden shadow-inner focus-within:border-blue-500/50 transition-colors">
                        <div className="text-slate-500 flex items-center justify-center pl-6">
                            <Search size={20} />
                        </div>
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="flex-1 bg-transparent border-none text-white focus:ring-0 px-6 text-xl font-light outline-none"
                            placeholder="Search movies, directors, or genres..."
                        />
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="bg-slate-800 text-slate-400 hover:text-white transition-colors rounded-lg px-4 py-2 m-2 gap-2 text-sm font-medium border border-slate-700 flex items-center disabled:opacity-50"
                        >
                            Return <CornerDownLeft size={16} />
                        </button>
                    </div>
                </form>
            </div>

            {/* AI Analysis Box */}
            {aiExplanation && !isLoading && !isError && (
                <div className="w-full max-w-4xl px-8 mt-8">
                    <div className="border-l-2 border-slate-500 bg-slate-900/50 p-4 font-mono text-sm text-slate-300 rounded-r-lg shadow-sm">
                        <span className="text-blue-400 font-bold mr-2">{'>'}</span> {aiExplanation}
                    </div>
                </div>
            )}

            {/* Results Bento Grid */}
            <div className="w-full max-w-6xl px-8 mt-12 pb-12">
                {isLoading ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                        {[...Array(10)].map((_, i) => (
                            <div key={i} className="aspect-[2/3] rounded-xl bg-slate-800/50 animate-pulse border border-slate-700/50"></div>
                        ))}
                    </div>
                ) : isError ? (
                    <div className="flex flex-col items-center justify-center p-12 border border-dashed border-slate-700 rounded-2xl bg-slate-900/30">
                        <AlertCircle size={48} className="text-red-500 mb-4" />
                        <h3 className="text-xl font-bold text-white mb-2">System Error</h3>
                        <p className="text-slate-400">Failed to connect to the recommendation engine. Please try again.</p>
                    </div>
                ) : hasSearched && recommendations.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-16 px-4 bg-slate-900/30 rounded-2xl border border-dashed border-slate-700 mx-8">
                        <div className="relative size-32 mb-2">
                            <div className="absolute inset-0 bg-blue-500/10 rounded-full blur-2xl"></div>
                            <div className="relative bg-slate-800 size-full rounded-full flex items-center justify-center shadow-lg border border-slate-700">
                                <Search className="text-6xl text-blue-500" size={48} />
                            </div>
                        </div>
                        <h3 className="text-white text-2xl font-bold mt-4">No movies found in this universe</h3>
                        <p className="text-slate-400 text-base mt-2">Try adjusting your filters or search query.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                        {recommendations.map((movie) => {
                            const poster = movie.poster_path || 'https://via.placeholder.com/500x750/1e293b/94a3b8?text=No+Poster';
                            const isExpanded = expandedId === movie.id;

                            return (
                                <div key={movie.id} className="relative group rounded-xl border border-slate-800 overflow-hidden bg-[#1a1f35] flex flex-col h-full transform transition-transform hover:scale-[1.02] hover:z-10 hover:shadow-2xl">
                                    {/* Poster Area */}
                                    <div className="relative aspect-[2/3] overflow-hidden">
                                        <img src={poster} alt={movie.title} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />

                                        {/* Hover Overlay */}
                                        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center gap-3 p-4">
                                            <button
                                                onClick={() => handleRate(movie.id, 'like', movie.title)}
                                                className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                                            >
                                                🔥 Love it
                                            </button>
                                            <button
                                                onClick={() => addToWatchlist(movie.id, movie.title)}
                                                className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                                            >
                                                📋 Watchlist
                                            </button>
                                            <button
                                                onClick={() => handleRate(movie.id, 'dislike', movie.title)}
                                                className="w-full py-2 bg-slate-800 border border-slate-600 hover:bg-slate-700 text-white font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                                            >
                                                👎 Pass
                                            </button>
                                        </div>

                                        {/* Meta badges */}
                                        <div className="absolute top-2 right-2 bg-black/80 backdrop-blur px-2 py-1 rounded text-xs font-bold text-yellow-500 flex items-center gap-1 border border-yellow-500/30">
                                            <Star size={12} fill="currentColor" /> {movie.rating?.toFixed(1) || 'N/A'}
                                        </div>
                                        {movie.match_score && (
                                            <div className="absolute top-2 left-2 bg-blue-600/90 backdrop-blur px-2 py-1 rounded text-xs font-bold text-white shadow-lg">
                                                {movie.match_score}% Match
                                            </div>
                                        )}
                                    </div>

                                    {/* Info Area */}
                                    <div className="p-3 flex flex-col flex-1 bg-gradient-to-t from-slate-900 to-slate-900/90 z-10">
                                        <h3 className="text-sm font-bold text-slate-100 line-clamp-1" title={movie.title}>{movie.title}</h3>

                                        {/* Expandable Synopsis Toggle */}
                                        <button
                                            onClick={() => setExpandedId(isExpanded ? null : movie.id)}
                                            className="text-xs text-slate-400 hover:text-white flex items-center gap-1 mt-2 focus:outline-none"
                                        >
                                            {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                                            {isExpanded ? 'Hide' : 'Synopsis'}
                                        </button>

                                        {/* Collapsible Overview Content */}
                                        <div className={`text-xs text-slate-400 mt-2 transition-all duration-300 overflow-hidden ${isExpanded ? 'max-h-48' : 'max-h-0'}`}>
                                            {movie.overview || 'No synopsis available.'}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Home;
