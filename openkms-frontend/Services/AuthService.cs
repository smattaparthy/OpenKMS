using Microsoft.JSInterop;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Localization;
using OpenKMS.Models.Requests;
using OpenKMS.Models.Responses;
using OpenKMS.Models;
using OpenKMS.Models.Enums;

namespace OpenKMS.Services
{
    public class AuthService : BaseApiService
    {
        private readonly IJSRuntime _jsRuntime;

        public AuthService(HttpClient httpClient, IConfiguration configuration, IJSRuntime jsRuntime)
            : base(httpClient, configuration)
        {
            _jsRuntime = jsRuntime;
        }

        public async Task<AuthResponse?> LoginAsync(UserLoginRequest loginRequest)
        {
            try
            {
                var response = await PostAsync<AuthResponse>("auth/login", loginRequest);
                if (response != null)
                {
                    await StoreTokens(response.AccessToken, response.RefreshToken);
                    SetAuthToken(response.AccessToken);
                }
                return response;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Login failed: {ex.Message}");
                throw;
            }
        }

        public async Task<AuthResponse?> RegisterAsync(UserCreateRequest registerRequest)
        {
            try
            {
                var response = await PostAsync<AuthResponse>("auth/register", registerRequest);
                if (response != null)
                {
                    await StoreTokens(response.AccessToken, response.RefreshToken);
                    SetAuthToken(response.AccessToken);
                }
                return response;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Registration failed: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> IsAuthenticatedAsync()
        {
            try
            {
                var token = await _jsRuntime.InvokeAsync<string>("localStorage.getItem", "accessToken");
                return !string.IsNullOrEmpty(token);
            }
            catch
            {
                return false;
            }
        }

        public async Task<string?> GetAccessTokenAsync()
        {
            try
            {
                return await _jsRuntime.InvokeAsync<string>("localStorage.getItem", "accessToken");
            }
            catch
            {
                return null;
            }
        }

        public async Task<User?> GetCurrentUserAsync()
        {
            try
            {
                var token = await GetAccessTokenAsync();
                if (!string.IsNullOrEmpty(token))
                {
                    return await GetAsync<User>("users/me");
                }
                return null;
            }
            catch
            {
                return null;
            }
        }

        public async Task InitializeAuthAsync()
        {
            var token = await GetAccessTokenAsync();
            if (!string.IsNullOrEmpty(token))
            {
                SetAuthToken(token);
            }
        }

        public async Task LogoutAsync()
        {
            await ClearTokensAsync();
            ClearAuthToken();
        }

        public async Task<AuthResponse?> RefreshTokenAsync()
        {
            try
            {
                var refreshToken = await _jsRuntime.InvokeAsync<string>("localStorage.getItem", "refreshToken");
                if (string.IsNullOrEmpty(refreshToken))
                {
                    return null;
                }

                var response = await PostAsync<AuthResponse>("auth/refresh", new { refreshToken = refreshToken });
                if (response != null)
                {
                    await StoreTokens(response.AccessToken, response.RefreshToken);
                    SetAuthToken(response.AccessToken);
                }
                return response;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Token refresh failed: {ex.Message}");
                await ClearTokensAsync();
                ClearAuthToken();
                return null;
            }
        }

        public async Task<bool> ChangePasswordAsync(string currentPassword, string newPassword)
        {
            try
            {
                var response = await PostAsync<object>("auth/change-password", new { currentPassword, newPassword });
                return response != null;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Password change failed: {ex.Message}");
                return false;
            }
        }

        private async Task StoreTokens(string accessToken, string refreshToken)
        {
            try
            {
                await _jsRuntime.InvokeVoidAsync("localStorage.setItem", "accessToken", accessToken);
                await _jsRuntime.InvokeVoidAsync("localStorage.setItem", "refreshToken", refreshToken);
            }
            catch (Exception ex)
            {
                // Handle JavaScript interop errors during static rendering
                Console.WriteLine($"Failed to store tokens in localStorage: {ex.Message}");
                // In static rendering, tokens will be stored after the component is fully interactive
                // Continue with the flow - the authentication will work once the page is fully loaded
            }
        }

        private async Task ClearTokensAsync()
        {
            try
            {
                await _jsRuntime.InvokeVoidAsync("localStorage.removeItem", "accessToken");
                await _jsRuntime.InvokeVoidAsync("localStorage.removeItem", "refreshToken");
            }
            catch (Exception ex)
            {
                // Handle JavaScript interop errors during static rendering
                Console.WriteLine($"Failed to clear tokens from localStorage: {ex.Message}");
                // Continue with the flow - tokens will be cleared when JavaScript is available
            }
        }
    }
}