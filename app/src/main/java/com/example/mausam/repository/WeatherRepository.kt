package com.example.mausam.repository

import com.example.mausam.data.remote.Weather
import com.example.mausam.data.remote.WeatherApi
import com.example.mausam.utils.Constants.API_KEY
import com.example.mausam.utils.Resource
import dagger.hilt.android.scopes.ActivityScoped
import javax.inject.Inject

@ActivityScoped
class WeatherRepository @Inject constructor(
    private val api: WeatherApi
) {
    suspend fun getWeatherInfo(
        lat: String,
        lon: String
    ): Resource<Weather> {
        val response = try {
            api.getWeather(lat, lon, API_KEY)
        } catch (e: Exception) {
            return Resource.Error("Unknown Error occurred.")
        }
        return Resource.Success(response)
    }
}