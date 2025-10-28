/**
 * Header Component
 * DiveTeacher branding and navigation
 */

import { brand } from '@/config/brand';
import { Waves } from 'lucide-react';

export function Header() {
  return (
    <header className="dive-header">
      <div className="dive-container">
        <div className="flex items-center gap-3">
          <Waves size={32} />
          <div>
            <h1 className="dive-header-title">{brand.name}</h1>
            <p className="dive-header-subtitle">{brand.tagline}</p>
          </div>
        </div>
      </div>
    </header>
  );
}

