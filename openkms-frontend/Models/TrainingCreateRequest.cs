using System.ComponentModel.DataAnnotations;

namespace OpenKMS.Models.Requests
{
    public class TrainingCreateRequest
    {
        [Required(ErrorMessage = "Title is required")]
        [StringLength(200, ErrorMessage = "Title cannot exceed 200 characters")]
        public string Title { get; set; } = "";

        [StringLength(2000, ErrorMessage = "Description cannot exceed 2000 characters")]
        public string? Description { get; set; }

        [Required(ErrorMessage = "Category is required")]
        public TrainingCategory Category { get; set; }

        [Required(ErrorMessage = "Level is required")]
        public TrainingLevel Level { get; set; } = TrainingLevel.BEGINNER;

        [Required(ErrorMessage = "Location is required")]
        [StringLength(100, ErrorMessage = "Location cannot exceed 100 characters")]
        public string Location { get; set; } = "";

        [Required(ErrorMessage = "Start date is required")]
        public DateTime StartDate { get; set; }

        [Required(ErrorMessage = "End date is required")]
        public DateTime EndDate { get; set; }

        [Required(ErrorMessage = "Duration is required")]
        [Range(0.5, 40, ErrorMessage = "Duration must be between 0.5 and 40 hours")]
        public float DurationHours { get; set; }

        [Required(ErrorMessage = "Maximum participants is required")]
        [Range(1, 1000, ErrorMessage = "Maximum participants must be between 1 and 1000")]
        public int MaxParticipants { get; set; } = 30;

        [Required(ErrorMessage = "Credits is required")]
        [Range(0, 20, ErrorMessage = "Credits must be between 0 and 20")]
        public int CreditsRequired { get; set; } = 1;

        [Range(0, 10000, ErrorMessage = "Cost must be between 0 and 10000")]
        public float Cost { get; set; } = 0.0f;

        [StringLength(100, ErrorMessage = "Instructor name cannot exceed 100 characters")]
        public string? Instructor { get; set; }

        [StringLength(1000, ErrorMessage = "Prerequisites cannot exceed 1000 characters")]
        public string? Prerequisites { get; set; }

        [StringLength(2000, ErrorMessage = "Learning objectives cannot exceed 2000 characters")]
        public string? LearningObjectives { get; set; }
    }

    public enum TrainingCategory
    {
        TECHNICAL,
        SOFT_SKILLS,
        COMPLIANCE,
        LEADERSHIP,
        SAFETY
    }

    public enum TrainingLevel
    {
        BEGINNER,
        INTERMEDIATE,
        ADVANCED,
        EXPERT
    }
}