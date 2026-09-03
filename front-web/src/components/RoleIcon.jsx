import * as Icons from "./icons";

export default function RoleIcon({ name, className = "h-5 w-5" }) {
  const Icon = Icons[name] || Icons.User;
  return <Icon className={className} />;
}
