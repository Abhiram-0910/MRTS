import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { Film, Home, Bookmark, Search } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

const Layout = () => {
    const { userId, setUserId, language, setLanguage } = useAppContext();

    return (
        <div className="flex h-screen w-full overflow-hidden bg-gradient-to-br from-slate-900 to-black text-slate-100 font-sans">
            <aside className="flex w-72 flex-col bg-slate-900/80 backdrop-blur-md border-r border-slate-800 h-full overflow-y-auto">
                <div className="flex items-center gap-3 p-6 shrink-0">
                    <div className="flex items-center justify-center size-10 rounded-lg bg-blue-600/20 text-blue-500 shadow-[0_0_15px_rgba(37,106,244,0.5)]">
                        <Film />
                    </div>
                    <h1 className="text-xl font-bold tracking-tight text-white drop-shadow-md">Movie & TV Shows Recommending Engine</h1>
                </div>
                <nav className="flex-1 flex flex-col gap-1 px-4 py-2">
                    <NavLink
                        to="/"
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                            }`
                        }
                    >
                        <Home size={20} />
                        <span className="font-medium text-sm">Home</span>
                    </NavLink>
                    <NavLink
                        to="/watchlist"
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                            }`
                        }
                    >
                        <Bookmark size={20} />
                        <span className="font-medium text-sm">Watchlist</span>
                    </NavLink>
                </nav>
                <div className="p-4 border-t border-slate-800 mt-auto shrink-0 flex flex-col gap-4">
                    <div className="flex flex-col gap-2">
                        <label className="text-xs font-medium text-slate-400 pl-1">User ID</label>
                        <input
                            type="text"
                            name="userId" // Added name attribute for accessibility/testing
                            className="w-full bg-slate-800/50 border border-slate-700 text-slate-100 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                            placeholder="e.g. user_8x9a"
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                        />
                    </div>
                    <div className="flex flex-col gap-2">
                        <label className="text-xs font-medium text-slate-400 pl-1">Language</label>
                        <select
                            title="Language Selection" // Added title attribute for accessibility
                            className="w-full bg-slate-800/50 border border-slate-700 text-slate-100 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 appearance-none"
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                        >
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="te">Telugu</option>
                        </select>
                    </div>
                </div>
            </aside>
            <main className="flex-1 flex flex-col h-full overflow-hidden relative">
                <header className="h-16 flex items-center justify-end px-8 border-b border-slate-800/50 bg-slate-900/30 backdrop-blur-sm z-10 shrink-0">
                    <div className="size-8 rounded-full bg-slate-700 border border-slate-600 overflow-hidden ml-2 flex items-center justify-center text-xs">
                        {userId.substring(0, 2).toUpperCase()}
                    </div>
                </header>
                <div className="flex-1 overflow-y-auto relative">
                    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-600/10 via-transparent to-transparent pointer-events-none"></div>
                    <div className="relative z-10">
                        <Outlet />
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Layout;
