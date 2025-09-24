using System.ComponentModel.DataAnnotations;

namespace OpenKMS.Models.Requests
{
    public class UserCreateRequest
    {
        [Required(ErrorMessage = "Username is required")]
        [StringLength(50, ErrorMessage = "Username cannot exceed 50 characters")]
        [RegularExpression("^[a-zA-Z0-9_]+$", ErrorMessage = "Username can only contain letters, numbers, and underscores")]
        public string Username { get; set; } = "";

        [Required(ErrorMessage = "Email is required")]
        [StringLength(100, ErrorMessage = "Email cannot exceed 100 characters")]
        [EmailAddress(ErrorMessage = "Invalid email format")]
        public string Email { get; set; } = "";

        [Required(ErrorMessage = "Full name is required")]
        [StringLength(100, ErrorMessage = "Full name cannot exceed 100 characters")]
        public string FullName { get; set; } = "";

        [Required(ErrorMessage = "Password is required")]
        [StringLength(100, MinimumLength = 8, ErrorMessage = "Password must be between 8 and 100 characters")]
        [RegularExpression(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]$",
            ErrorMessage = "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character")]
        public string Password { get; set; } = "";

        [Required(ErrorMessage = "Confirm password is required")]
        [Compare("Password", ErrorMessage = "Passwords do not match")]
        public string ConfirmPassword { get; set; } = "";

        [Required(ErrorMessage = "Role is required")]
        public UserRole Role { get; set; } = UserRole.EMPLOYEE;

        [StringLength(50, ErrorMessage = "Department cannot exceed 50 characters")]
        public string? Department { get; set; }

        [StringLength(50, ErrorMessage = "Office location cannot exceed 50 characters")]
        public string? OfficeLocation { get; set; }

        [Required(ErrorMessage = "Account status is required")]
        public bool IsActive { get; set; } = true;
    }

    public enum UserRole
    {
        EMPLOYEE,
        KNOWLEDGE_MANAGER,
        ADMIN
    }
}