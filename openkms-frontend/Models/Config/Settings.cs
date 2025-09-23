namespace OpenKMS.Models.Config
{
    public class ApiSettings
    {
        public string BaseUrl { get; set; } = string.Empty;
        public string Version { get; set; } = "v1";
        public int TimeoutSeconds { get; set; } = 30;
    }

    public class ApplicationSettings
    {
        public string Name { get; set; } = "OpenKMS";
        public ThemeSettings Theme { get; set; } = new();
    }

    public class ThemeSettings
    {
        public string PrimaryNavy { get; set; } = "#003366";
        public string Cream { get; set; } = "#FFF8DC";
        public string LightBlue { get; set; } = "#E6F2FF";
        public string DarkBlue { get; set; } = "#002244";
        public string Gold { get; set; } = "#FFD700";
    }
}