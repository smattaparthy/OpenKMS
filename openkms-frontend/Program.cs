using openkms_frontend.Components;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.JSInterop;
using OpenKMS.Services;
using OpenKMS.Models.Config;
using OpenKMS.Handlers;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

// Add configuration
builder.Services.Configure<ApiSettings>(builder.Configuration.GetSection("ApiSettings"));
builder.Services.Configure<ApplicationSettings>(builder.Configuration.GetSection("ApplicationSettings"));

// Add HTTP client with AuthDelegatingHandler
builder.Services.AddHttpClient<AuthService>(client =>
{
    var configuration = builder.Configuration;
    var baseUrl = $"{configuration["ApiSettings:BaseUrl"]}/api/{configuration["ApiSettings:Version"]}";
    client.BaseAddress = new Uri(baseUrl);
    client.DefaultRequestHeaders.Accept.Clear();
    client.DefaultRequestHeaders.Accept.Add(new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue("application/json"));
    client.Timeout = TimeSpan.FromSeconds(configuration.GetValue<int>("ApiSettings:TimeoutSeconds"));
})
.AddHttpMessageHandler<AuthDelegatingHandler>();

// Add AuthDelegatingHandler
builder.Services.AddScoped<AuthDelegatingHandler>();

// Add services - this creates the circular dependency issue, so we need to fix it
builder.Services.AddScoped<AuthService>(sp =>
{
    var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();
    var configuration = sp.GetRequiredService<IConfiguration>();
    var jsRuntime = sp.GetRequiredService<IJSRuntime>();
    return new AuthService(httpClientFactory.CreateClient(), configuration, jsRuntime);
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();

app.UseStaticFiles();
app.UseAntiforgery();

app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
