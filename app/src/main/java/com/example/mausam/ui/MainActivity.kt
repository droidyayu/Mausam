package com.example.mausam.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.material.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.mausam.R
import com.example.mausam.ui.navdrawer.Drawer
import com.example.mausam.ui.navdrawer.NavDrawerItem
import com.example.mausam.ui.ui.theme.DhoopTheme
import com.example.mausam.ui.weather.WeatherScreen
import com.example.mausam.ui.weatherdetail.WeatherDetailScreen
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            DhoopTheme {
                MausamMainScreen()
            }
        }
    }
}

@Composable
@Preview(showBackground = true)
fun MausamMainScreen() {
    val scaffoldState = rememberScaffoldState(rememberDrawerState(DrawerValue.Closed))
    val scope = rememberCoroutineScope()
    val navController = rememberNavController()

    Scaffold(
        scaffoldState = scaffoldState,
        topBar = { TopBar(scope = scope, scaffoldState = scaffoldState) },
        drawerBackgroundColor = Color.White,
        drawerContent = {
            Drawer(
                scope = scope,
                scaffoldState = scaffoldState,
                navController = navController
            )
        }
    ) { paddingValues ->
        Navigation(navController = navController, paddingValues = paddingValues)
    }
}

@Composable
fun TopBar(
    scope: CoroutineScope,
    scaffoldState: ScaffoldState
) {
    TopAppBar(
        title = {
            Box(
                Modifier.fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = stringResource(R.string.current_location_string),
                    style = MaterialTheme.typography.h6,
                    maxLines = 1,
                    color = Color.White,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(end = 64.dp)
                )
            }
        },
        navigationIcon = {
            IconButton(onClick = {
                scope.launch {
                    scaffoldState.drawerState.open()
                }
            }) {
                Icon(
                    painter = painterResource(id = R.drawable.ic_menu),
                    contentDescription = stringResource(R.string.description),
                    tint = Color.White
                )
            }
        },
        backgroundColor = Color.Transparent,
        contentColor = Color.White,
        elevation = 0.dp,
    )
}

@Composable
fun Navigation(
    navController: NavHostController,
    paddingValues: PaddingValues
) {
    NavHost(navController, startDestination = NavDrawerItem.Home.route, Modifier.padding(paddingValues)) {
        composable(NavDrawerItem.Home.route) {
            WeatherScreen()
        }
        composable(NavDrawerItem.NextSevenDays.route) {
            WeatherDetailScreen()
        }
    }
}
