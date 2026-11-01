/// Повертає непорожнє ім’я або значення за замовчуванням.
func displayName(for name: String?) -> String {
    guard let name = name, !name.isEmpty else {
        return "Гість"
    }
    return name
}
