import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { ROLE_LABELS } from "../lib/constants";
import RoleIcon from "./RoleIcon";
import Logo from "./Logo";
import { LayoutDashboard, MessageCircle, Shield, LogOut } from "./icons";

const navItems = [
  { to: "/dashboard", label: "Panel", Icon: LayoutDashboard },
  { to: "/chat", label: "Asistente", Icon: MessageCircle },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isAdmin = user?.role === "admin";

  return (
    <header className="sticky top-0 z-50 border-b-2 border-eco-100 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">
        <Link to="/dashboard">
          <Logo size="md" />
        </Link>

        <nav className="flex items-center gap-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-lg px-4 py-2.5 text-base font-medium transition-colors ${
                  isActive
                    ? "bg-eco-100 text-eco-700"
                    : "text-gray-600 hover:bg-eco-50 hover:text-eco-600"
                }`
              }
            >
              <item.Icon className="h-5 w-5" />
              {item.label}
            </NavLink>
          ))}
          {isAdmin && (
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-lg px-4 py-2.5 text-base font-medium transition-colors ${
                  isActive
                    ? "bg-eco-100 text-eco-700"
                    : "text-gray-600 hover:bg-eco-50 hover:text-eco-600"
                }`
              }
            >
              <Shield className="h-5 w-5" />
              Admin
            </NavLink>
          )}
        </nav>

        <div className="flex items-center gap-4">
          {user && (
            <div className="flex items-center gap-2">
              <RoleIcon
                name={user.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : "User"}
                className="h-5 w-5 text-gray-500"
              />
              <div className="hidden text-right sm:block">
                <p className="text-sm font-medium text-gray-700">
                  {user.companyName || user.email}
                </p>
                <p className="text-xs text-gray-400">
                  {ROLE_LABELS[user.role] || "Usuario"}
                </p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50"
          >
            <LogOut className="h-4 w-4" />
            Salir
          </button>
        </div>
      </div>
    </header>
  );
}
