import React from 'react';

const MetricCard = ({ title, value, icon: Icon, trend }) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md transition-shadow">
      <div>
        <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
        <h3 className="text-3xl font-bold text-brand-dark">{value}</h3>
        {trend !== undefined && (
          <p className={`text-xs mt-2 font-medium ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '+' : ''}{trend}% vs mes anterior
          </p>
        )}
      </div>
      <div className="p-3 bg-gray-50 rounded-full text-black">
        <Icon size={28} strokeWidth={1.5} />
      </div>
    </div>
  );
};

export default MetricCard;