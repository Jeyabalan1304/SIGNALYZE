import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileCheck, Database, Settings, LogOut, Search, PlusCircle, UploadCloud } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import VerifyData from './pages/VerifyData';
import UploadSingle from './pages/UploadSingle';
import UploadCSV from './pages/UploadCSV';

const SidebarLink = ({ to, icon: Icon, label }: { to: string, icon: any, label: string }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link 
      to={to} 
      className={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 ${
        isActive 
          ? 'bg-primary-600 text-white shadow-md' 
          : 'text-gray-500 hover:bg-gray-100'
      }`}
    >
      <Icon className="w-5 h-5 mr-3" />
      <span className="font-medium text-sm">{label}</span>
    </Link>
  );
};

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50 font-sans antialiased">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r flex flex-col fixed inset-y-0 shadow-sm z-50">
          <div className="p-8">
            <h1 className="text-2xl font-black text-primary-600 tracking-tighter italic text-blue-600">SIGNALYZE</h1>
            <p className="text-[10px] uppercase font-bold text-gray-400 tracking-widest mt-1">Intelligence Layer v1.4</p>
          </div>
          
          <nav className="flex-1 px-4 space-y-1">
            <SidebarLink to="/" icon={LayoutDashboard} label="Dashboard" />
            <SidebarLink to="/upload-single" icon={PlusCircle} label="Single Ingestion" />
            <SidebarLink to="/upload-csv" icon={UploadCloud} label="Bulk Ingestion" />
            <SidebarLink to="/verify" icon={FileCheck} label="Verification View" />
            <SidebarLink to="/data" icon={Database} label="Raw Storage" />
            <SidebarLink to="/settings" icon={Settings} label="Settings" />
          </nav>

          <div className="p-4 border-t">
            <button className="flex items-center w-full px-4 py-3 text-gray-500 hover:text-rose-600 transition">
              <LogOut className="w-5 h-5 mr-3" />
              <span className="font-medium text-sm">Sign Out</span>
            </button>
          </div>
        </aside>

        {/* Top Navbar */}
        <div className="flex-1 flex flex-col ml-64">
          <header className="h-16 bg-white border-b px-8 flex items-center justify-between sticky top-0 z-40">
            <div className="relative w-96">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input 
                type="text" 
                placeholder="Global search across insights..." 
                className="w-full pl-10 pr-4 py-1.5 bg-gray-50 border-none rounded-full text-sm focus:ring-1 focus:ring-primary-500 transition" 
              />
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold text-xs ring-2 ring-white shadow-sm border">
                JP
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="p-8 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload-single" element={<UploadSingle />} />
              <Route path="/upload-csv" element={<UploadCSV />} />
              <Route path="/verify" element={<VerifyData />} />
              <Route path="*" element={<Dashboard />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
