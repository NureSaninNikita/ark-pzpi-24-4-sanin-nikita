/// Перевіряє право реєстрації за віком.
/// - Parameter age: Вік користувача у повних роках.
/// - Returns: true, якщо віку достатньо для реєстрації.
func canRegister(age: Int) -> Bool {
    let minimumAge = 18
    return age >= minimumAge
}
