import { useNavigate } from "react-router-dom";
import "./sidebar.css";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Building2,
  Users,
  UserRoundCheck,
  Wallet,
  ArrowLeftRight,
  LogOut
} from "lucide-react";

function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login", { replace: true });
  };
  return (
    <aside className="sidebar">

      {/* Logo */}
      <div className="sidebar-logo">
        <h2>LeoPay</h2>
        <p>Admin Panel</p>
      </div>

      {/* Navigation Menu */}
      <nav className="sidebar-menu">

        <NavLink to="/dashboard" className="menu-item">
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/organizations" className="menu-item">
          <Building2 size={20} />
          <span>Organizations</span>
        </NavLink>

        <a href="#" className="menu-item">
          <Users size={20} />
          <span>Remitters</span>
        </a>

        <a href="#" className="menu-item">
          <UserRoundCheck size={20} />
          <span>Beneficiaries</span>
        </a>

        <a href="#" className="menu-item">
          <Wallet size={20} />
          <span>Wallets</span>
        </a>

        <a href="#" className="menu-item">
          <ArrowLeftRight size={20} />
          <span>Payouts</span>
        </a>

      </nav>


      {/* Logout */}
      <div className="sidebar-bottom">
        <button
          type="button"
          className="menu-item logout-btn"
          onClick={handleLogout}
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>

    </aside>
  );
}

export default Sidebar;