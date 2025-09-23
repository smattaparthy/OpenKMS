namespace OpenKMS.Models.Responses
{
    public class AuthResponse
    {
        public string AccessToken { get; set; } = string.Empty;
        public string RefreshToken { get; set; } = string.Empty;
        public string TokenType { get; set; } = "bearer";
        public User User { get; set; } = new();
    }
}