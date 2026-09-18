import React, { useState, useRef, useEffect } from 'react';
import { Calendar, ChevronDown } from 'lucide-react';

export default function PeriodSelector({ value, onChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const [view, setView] = useState('years'); // 'years' | 'months'
  const [tempYear, setTempYear] = useState(null);
  const dropdownRef = useRef(null);

  // Parse current value
  const currentYear = value ? value.substring(0, 4) : '';
  const currentMonth = value ? value.substring(4, 6) : '';

  const todayYear = new Date().getFullYear();
  // Ensure we show up to 2026 if todayYear is less (based on previous hardcoded 2025-2026)
  const baseYear = Math.max(todayYear, 2026); 
  const years = Array.from({ length: 9 }, (_, i) => baseYear - i);

  const months = [
    { num: '01', name: 'Ene' }, { num: '02', name: 'Feb' }, { num: '03', name: 'Mar' },
    { num: '04', name: 'Abr' }, { num: '05', name: 'May' }, { num: '06', name: 'Jun' },
    { num: '07', name: 'Jul' }, { num: '08', name: 'Ago' }, { num: '09', name: 'Sep' },
    { num: '10', name: 'Oct' }, { num: '11', name: 'Nov' }, { num: '12', name: 'Dic' }
  ];

  const monthNamesFull = {
    '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
    '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
    '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
  };

  const getDisplayValue = () => {
    if (!value) return 'Seleccionar...';
    return `${monthNamesFull[currentMonth]} ${currentYear}`;
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setTimeout(() => setView('years'), 200);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleYearClick = (year) => {
    setTempYear(year);
    setView('months');
  };

  const handleMonthClick = (monthNum) => {
    const newPeriod = `${tempYear}${monthNum}`;
    onChange(newPeriod);
    setIsOpen(false);
    setTimeout(() => setView('years'), 200); // reset after closing
  };

  return (
    <div className="period-selector-container" ref={dropdownRef}>
      <div 
        className={`period-selector-input ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <Calendar size={16} className="ps-icon" />
        <span className="ps-value">{getDisplayValue()}</span>
        <ChevronDown size={16} className="ps-chevron" />
      </div>

      {isOpen && (
        <div className="period-selector-popup">
          {view === 'years' ? (
            <>
              <div className="ps-header">Selecciona el Año</div>
              <div className="ps-grid ps-grid-years">
                {years.map(year => (
                  <button 
                    key={year} 
                    className={`ps-btn ${currentYear === String(year) ? 'selected' : ''}`}
                    onClick={() => handleYearClick(year)}
                  >
                    {year}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              <div className="ps-header">
                <button className="ps-back-btn" onClick={() => setView('years')}>←</button>
                <span>Año {tempYear}</span>
              </div>
              <div className="ps-grid ps-grid-months">
                {months.map(m => {
                  const isSelected = currentYear === String(tempYear) && currentMonth === m.num;
                  return (
                    <button 
                      key={m.num} 
                      className={`ps-btn ${isSelected ? 'selected' : ''}`}
                      onClick={() => handleMonthClick(m.num)}
                    >
                      {m.name}
                    </button>
                  )
                })}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
