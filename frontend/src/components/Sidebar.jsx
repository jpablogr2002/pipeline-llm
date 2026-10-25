import React from 'react';
import { MessageSquare, LayoutDashboard, LogOut } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Chat Agente', path: '/chat', icon: MessageSquare },
  ];

  return (
    <div className="w-64 h-screen bg-brand-dark text-white flex flex-col shadow-lg">
      <div className="p-6">
        <h1 className="text-2xl font-bold tracking-wider text-brand-light">MediaGroup</h1>
        <p className="text-sm text-brand-pale opacity-80">Pipeline Inteligente</p>
      </div>
      
      <nav className="flex-1 mt-6">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center px-6 py-4 transition-colors ${
                isActive ? 'bg-brand-blue text-white border-l-4 border-brand-cyan' : 'text-brand-pale hover:bg-brand-blue/50'
              }`}
            >
              <Icon size={20} className="mr-3" />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-brand-blue/30">
        <button className="flex items-center text-brand-pale hover:text-white transition-colors">
          <LogOut size={20} className="mr-3" />
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;