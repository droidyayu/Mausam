package com.example.mausam.ui.navdrawer

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Dashboard
import androidx.compose.material.icons.rounded.Home
import androidx.compose.material.icons.rounded.NextWeek
import androidx.compose.material.icons.rounded.Thermostat
import androidx.compose.ui.graphics.vector.ImageVector

sealed class NavDrawerItem(
    var route: String,
    var icon: ImageVector,
    var title: String
) {
    object Home : NavDrawerItem("home", Icons.Rounded.Home, "Dashboard")
    object NextSevenDays : NavDrawerItem("nextSevenDays", Icons.Rounded.NextWeek, "Forecast")
}