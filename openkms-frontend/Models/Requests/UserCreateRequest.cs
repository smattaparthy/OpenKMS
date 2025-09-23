namespace OpenKMS.Models.Requests
{
    public class UserCreateRequest
    {
        public string Username { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string FullName { get; set; } = string.Empty;
        public string? OfficeLocation { get; set; }
        public string? Department { get; set; }
        public string Password { get; set; } = string.Empty;
    }
}