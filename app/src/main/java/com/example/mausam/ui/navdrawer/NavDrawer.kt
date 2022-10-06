package com.example.mausam.ui.navdrawer

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.Divider
import androidx.compose.material.Icon
import androidx.compose.material.ScaffoldState
import androidx.compose.material.Text
import com.example.mausam.R
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.colorResource
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import androidx.navigation.compose.currentBackStackEntryAsState
import com.example.mausam.ui.ui.theme.Vazir
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

@Composable
fun Drawer(scope: CoroutineScope, scaffoldState: ScaffoldState, navController: NavController) {
    val items = listOf(
        NavDrawerItem.Home,
        NavDrawerItem.NextSevenDays,
    )
    Column(
        modifier = Modifier.background(Color(0, 0, 0, 0))
    ) {
        val centralHorizontalModifier = Modifier
            .padding(12.dp)
            .align(Alignment.CenterHorizontally)

        getCentralImage()
        getCentralImageText(
            centralHorizontalModifier,
            FontWeight.ExtraBold,
            24.sp,
            stringResource(R.string.app_name)
        )
        getSpacer()
        getDivider()

        val navBackStackEntry by navController.currentBackStackEntryAsState()
        val currentRoute = navBackStackEntry?.destination?.route
        items.forEach { item ->
            DrawerItem(item = item,
                selected = currentRoute == item.route,
                onItemClick = {
                    navigateToDestination(navController, item)
                    scope.launch {
                        scaffoldState.drawerState.close()
                    }
                })
        }

        Spacer(modifier = Modifier.weight(1f))

        getCentralImageText(
            modifier = centralHorizontalModifier,
            fontWeight = FontWeight.Medium,
            fontSize = 10.sp,
            text = stringResource(R.string.developer_name)
        )
    }
}

private fun navigateToDestination(
    navController: NavController,
    item: NavDrawerItem
) {
    navController.navigate(item.route) {
        navController.graph.startDestinationRoute?.let { route ->
            popUpTo(route) {
                saveState = true
            }
        }
        launchSingleTop = true
        restoreState = true
    }
}

@Composable
fun DrawerItem(item: NavDrawerItem, selected: Boolean, onItemClick: (NavDrawerItem) -> Unit) {
    val background = if (selected) R.color.purple_200 else android.R.color.transparent
    val textColor = if (selected) Color.White else Color.Black
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = { onItemClick(item) })
            .height(45.dp)
            .background(colorResource(id = background))
            .padding(start = 10.dp)
    ) {
        Icon(
            item.icon,
            contentDescription = item.title,
            modifier = Modifier
                .height(22.dp)
                .width(22.dp),
            Color.Black
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = item.title,
            color = textColor,
            textAlign = TextAlign.Start,
            fontSize = 14.sp,
            fontFamily = Vazir,
        )
    }
}

@Composable
@Preview
fun getCentralImage() {
    Image(
        painter = painterResource(id = R.drawable.ic_app_round),
        contentDescription = R.string.description.toString(),
        modifier = Modifier
            .fillMaxWidth()
            .padding(PaddingValues(8.dp, 48.dp, 8.dp, 8.dp))
            .size(80.dp)
    )
}

@Composable
fun getCentralImageText(
    modifier: Modifier,
    fontWeight: FontWeight,
    fontSize: TextUnit,
    text: String
) {
    Text(
        text = text,
        color = Color.Black,
        textAlign = TextAlign.Center,
        fontWeight = fontWeight,
        modifier = modifier,
        fontSize = fontSize
    )
}

@Composable
@Preview
fun getSpacer() {
    Spacer(
        modifier = Modifier
            .fillMaxWidth()
            .height(12.dp)
    )
}

@Composable
@Preview
fun getDivider() {
    Divider(
        modifier = Modifier
            .fillMaxWidth()
            .height(2.dp)
            .padding(0.dp, 16.dp)
    )
}