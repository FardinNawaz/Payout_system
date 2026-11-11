import { UserCircle } from "lucide-react";
import "./Header.css";

function Header() {
  return (
    <header className="header">

      <div className="header-title">
        <h2>Dashboard</h2>
        <p>Welcome back, Admin!</p>
      </div>

      <div className="header-actions">
        <div className="admin-profile">
          <UserCircle size={30} />
          <span>Admin</span>
        </div>
      </div>

    </header>
  );
}

export default Header;