package com.example.mausam.ui.weather

import android.content.Intent
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Alignment.Companion.CenterHorizontally
import androidx.compose.ui.Alignment.Companion.CenterVertically
import androidx.compose.ui.Alignment.Companion.TopEnd
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.mausam.R
import com.example.mausam.ui.LeakingActivity
import com.example.mausam.utils.getImageFromUrl
import timber.log.Timber

@Composable
fun WeatherScreen(viewModel: WeatherViewModel = hiltViewModel()) {
    val scrollStateScreen = rememberScrollState()
    val isLoading by remember { viewModel.isLoading }
    val loadError by remember { viewModel.loadError }

    if (isDataFetched(isLoading, loadError)) {
        ShowDataView(scrollStateScreen, viewModel)
    } else if (loadError.isNotEmpty()) {
        RetrySection(error = loadError) {
            viewModel.loadCurrentWeatherData()
            viewModel.loadHourlyWeatherData()
        }
    } else {
        Column(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = CenterHorizontally
        ) {
            CircularProgressIndicator(color = Color.Cyan)
        }
    }
}

@Composable
private fun ShowDataView(scrollStateScreen: ScrollState, viewModel: WeatherViewModel) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollStateScreen)
    ) {
        Column(
            modifier = Modifier
                .align(Alignment.TopStart)
                .fillMaxWidth()
        ) {
            CurrentWeatherData(viewModel = viewModel)
            GetDivider()
            Row(
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier
                    .padding(16.dp)
                    .fillMaxWidth(),
                verticalAlignment = CenterVertically
            ) {
                Text(
                    text = stringResource(R.string.later_today_text),
                    fontSize = 24.sp,
                    textAlign = TextAlign.Start,
                    color = Color.White
                )
            }
            HourlyWeatherList()
        }
        val context = LocalContext.current

        OutlinedButton(
            onClick = {
                context.startActivity(
                    Intent(
                        context,
                        LeakingActivity::class.java
                    )
                )
            },
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomEnd)
        ) {
            Text(
                text = "Click to open leak screen",
                modifier = Modifier
                    .wrapContentWidth()
                    .wrapContentHeight(), textAlign = TextAlign.Center, fontSize = 20.sp
            )
        }
    }
}


@Composable
@Preview
fun GetDivider() {
    Divider(
        color = Color.White,
        modifier = Modifier
            .fillMaxWidth()
            .padding(0.dp, 40.dp)
    )
}

@Composable
fun CurrentWeatherData(viewModel: WeatherViewModel) {
    val currentImgUrl by remember { viewModel.currentImgUrl }
    Box(
        modifier = Modifier
            .fillMaxSize()
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
        ) {
            CurrentDateBox()
            CurrentWeatherBox()
        }

        Image(
            painter = painterResource(id = getImageFromUrl(currentImgUrl)),
            contentDescription = stringResource(R.string.description),
            modifier = Modifier
                .size(80.dp)
                .align(TopEnd)
                .padding(16.dp, 16.dp, 16.dp, 0.dp)
        )
    }

}

@Composable
fun HourlyWeatherList(viewModel: WeatherViewModel = hiltViewModel()) {
    val hourlyWeatherList by remember { viewModel.hourlyWeatherList }
    val isLoading by remember { viewModel.isLoading }

    LazyRow {
        items(hourlyWeatherList) {
            if (!isLoading) {
                HourlyWeatherBox(
                    time = it.time,
                    imgUrl = it.imgUrl,
                    temp = it.temp
                )
            }
        }
    }
}

@Composable
fun HourlyWeatherBox(
    time: String,
    imgUrl: String,
    temp: String
) {
    Box(modifier = Modifier.padding(4.dp, 4.dp)) {
        Box(
            modifier = Modifier
                .wrapContentWidth()
                .wrapContentHeight()
                .clip(RoundedCornerShape(5.dp))
                .padding(4.dp, 4.dp)
                .border(width = 1.dp, color = Color.White)

        ) {
            Column(
                modifier = Modifier.padding(8.dp, 8.dp),
                horizontalAlignment = CenterHorizontally
            ) {
                Text(
                    text = time,
                    color = Color.White,
                    fontSize = 18.sp,
                    textAlign = TextAlign.Center,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(PaddingValues(0.dp, 8.dp, 0.dp, 8.dp))
                )

                Row(verticalAlignment = CenterVertically) {
                    Image(
                        painter = painterResource(id = getImageFromUrl(imgUrl)),
                        contentDescription = stringResource(R.string.description),
                        modifier = Modifier.size(32.dp)
                    )
                    Text(
                        text = temp,
                        color = Color.White,
                        fontSize = 18.sp,
                        modifier = Modifier.padding(8.dp, 0.dp)
                    )
                }
            }
        }
    }
}


fun isDataFetched(isLoading: Boolean, loadError: String): Boolean {
    return !isLoading && loadError.isEmpty()
}

@Composable
fun CurrentDateBox(viewModel: WeatherViewModel = hiltViewModel()) {
    val currentDate by remember { viewModel.currentDate }
    val isLoading by remember { viewModel.isLoading }
    val loadingError by remember { viewModel.loadError }

    if (isDataFetched(isLoading, loadingError)) {
        Row(
            modifier = Modifier.fillMaxSize(),
        ) {
            Text(
                text = currentDate,
                color = Color.White,
                fontSize = MaterialTheme.typography.body1.fontSize,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp, 16.dp, 16.dp, 0.dp)
            )
        }
    } else {
        Timber.e(loadingError)
    }
}

@Composable
fun CurrentWeatherBox(viewModel: WeatherViewModel = hiltViewModel()) {
    val currentTemp by remember { viewModel.currentTemp }
    val currentWeatherType by remember { viewModel.currentWeatherType }
    val currentHumidity by remember { viewModel.currentHumidity }
    val currentUV by remember { viewModel.currentUV }
    val isLoading by remember { viewModel.isLoading }

    if (!isLoading) {
        Box(
            modifier = Modifier
                .clip(RoundedCornerShape(20.dp))
                .padding(16.dp, 0.dp, 16.dp, 0.dp)
        ) {
            Column {
                Text(
                    text = "$currentWeatherType $currentTemp",
                    color = Color.White,
                    fontSize = MaterialTheme.typography.h5.fontSize,
                    textAlign = TextAlign.Start,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(0.dp, 8.dp, 0.dp, 0.dp)
                )

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(0.dp, 16.dp, 0.dp, 0.dp)
                ) {
                    Row(
                        Modifier.weight(1f),
                        verticalAlignment = CenterVertically
                    ) {
                        Image(
                            painter = painterResource(id = R.drawable.ic_humidity),
                            contentDescription = stringResource(R.string.description)
                        )
                        Text(
                            text = "Humidity $currentHumidity",
                            color = Color.White,
                            modifier = Modifier
                                .padding(12.dp, 12.dp),
                            fontSize = 18.sp
                        )
                    }
                    Row(
                        Modifier.weight(1f),
                        verticalAlignment = CenterVertically
                    ) {
                        Image(
                            painter = painterResource(id = R.drawable.ic_wind),
                            contentDescription = stringResource(R.string.description)
                        )
                        Text(
                            text = "UV $currentUV",
                            color = Color.White,
                            modifier = Modifier
                                .padding(12.dp, 12.dp),
                            fontSize = 18.sp
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun RetrySection(
    error: String,
    onRetry: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(error, color = Color.Red, fontSize = 18.sp)
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = { onRetry() },
            modifier = Modifier.align(CenterHorizontally)
        ) {
            Text(text = stringResource(R.string.retry_text), color = Color.White)
        }
    }
}

