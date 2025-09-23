using System.Net.Http.Headers;
using System.Text;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using OpenKMS.Models.Responses;

namespace OpenKMS.Services
{
    public abstract class BaseApiService
    {
        protected readonly HttpClient _httpClient;
        protected readonly IConfiguration _configuration;
        protected readonly string _apiBaseUrl;

        protected BaseApiService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _configuration = configuration;
            _apiBaseUrl = $"{_configuration["ApiSettings:BaseUrl"]}/api/{_configuration["ApiSettings:Version"]}";

            _httpClient.BaseAddress = new Uri(_apiBaseUrl);
            _httpClient.DefaultRequestHeaders.Accept.Clear();
            _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            _httpClient.Timeout = TimeSpan.FromSeconds(_configuration.GetValue<int>("ApiSettings:TimeoutSeconds"));
        }

        protected void SetAuthToken(string token)
        {
            _httpClient.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", token);
        }

        protected void ClearAuthToken()
        {
            _httpClient.DefaultRequestHeaders.Authorization = null;
        }

        protected async Task<T?> GetAsync<T>(string endpoint)
        {
            var response = await _httpClient.GetAsync(endpoint);
            return await HandleResponse<T>(response);
        }

        protected async Task<T?> PostAsync<T>(string endpoint, object? data = null)
        {
            var content = data != null
                ? new StringContent(JsonConvert.SerializeObject(data), Encoding.UTF8, "application/json")
                : null;

            var response = await _httpClient.PostAsync(endpoint, content);
            return await HandleResponse<T>(response);
        }

        protected async Task<T?> PutAsync<T>(string endpoint, object? data = null)
        {
            var content = data != null
                ? new StringContent(JsonConvert.SerializeObject(data), Encoding.UTF8, "application/json")
                : null;

            var response = await _httpClient.PutAsync(endpoint, content);
            return await HandleResponse<T>(response);
        }

        protected async Task<T?> DeleteAsync<T>(string endpoint)
        {
            var response = await _httpClient.DeleteAsync(endpoint);
            return await HandleResponse<T>(response);
        }

        private async Task<T?> HandleResponse<T>(HttpResponseMessage response)
        {
            if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                throw new HttpRequestException("Authentication required");
            }

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException($"API request failed: {response.StatusCode} - {errorContent}");
            }

            var content = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<T>(content);
        }
    }
}