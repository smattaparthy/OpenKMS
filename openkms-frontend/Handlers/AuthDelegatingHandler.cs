using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.JSInterop;
using OpenKMS.Services;

namespace OpenKMS.Handlers
{
    // Define AuthResponse class to match the one in Models.Responses
    public class AuthResponse
    {
        public string AccessToken { get; set; } = string.Empty;
        public string RefreshToken { get; set; } = string.Empty;
        public string TokenType { get; set; } = "bearer";
    }

    public class AuthDelegatingHandler : DelegatingHandler
    {
        private readonly IConfiguration _configuration;
        private readonly IJSRuntime _jsRuntime;

        public AuthDelegatingHandler(IConfiguration configuration, IJSRuntime jsRuntime)
        {
            _configuration = configuration;
            _jsRuntime = jsRuntime;
        }

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            // Try to get token and add to request
            var token = await _jsRuntime.InvokeAsync<string>("localStorage.getItem", "accessToken");
            if (!string.IsNullOrEmpty(token))
            {
                request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
            }

            var response = await base.SendAsync(request, cancellationToken);

            // If unauthorized, try to refresh token and retry
            if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                var refreshToken = await _jsRuntime.InvokeAsync<string>("localStorage.getItem", "refreshToken");
                if (!string.IsNullOrEmpty(refreshToken))
                {
                    // Try to refresh token using a simple HTTP client
                    var baseUrl = $"{_configuration["ApiSettings:BaseUrl"]}/api/{_configuration["ApiSettings:Version"]}";
                    using var refreshClient = new HttpClient();
                    refreshClient.BaseAddress = new Uri(baseUrl);

                    var refreshResponse = await refreshClient.PostAsJsonAsync("auth/refresh", new { refreshToken });
                    if (refreshResponse.IsSuccessStatusCode)
                    {
                        var refreshResult = await refreshResponse.Content.ReadFromJsonAsync<AuthResponse>();
                        if (refreshResult != null)
                        {
                            // Store new tokens
                            await _jsRuntime.InvokeVoidAsync("localStorage.setItem", "accessToken", refreshResult.AccessToken);
                            await _jsRuntime.InvokeVoidAsync("localStorage.setItem", "refreshToken", refreshResult.RefreshToken);

                            // Get new token and retry request
                            var newToken = refreshResult.AccessToken;
                            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", newToken);

                            // Clone the request since it can't be sent again
                            var newRequest = await CloneRequest(request);
                            response = await base.SendAsync(newRequest, cancellationToken);
                        }
                    }
                }
            }

            return response;
        }

        private async Task<HttpRequestMessage> CloneRequest(HttpRequestMessage request)
        {
            var clone = new HttpRequestMessage(request.Method, request.RequestUri);

            // Copy content
            if (request.Content != null)
            {
                clone.Content = await request.Content.ReadAsStreamAsync();
                clone.Content.Headers.ContentType = request.Content.Headers.ContentType;
            }

            // Copy headers
            foreach (var header in request.Headers)
            {
                clone.Headers.TryAddWithoutValidation(header.Key, header.Value);
            }

            return clone;
        }
    }
}