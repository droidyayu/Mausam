package com.example.mausam

import android.app.Application
import com.example.mausam.leak.LeakCanaryUploadService
import dagger.hilt.android.HiltAndroidApp
import leakcanary.EventListener
import leakcanary.LeakCanary

@HiltAndroidApp
class MausamApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        val analysisUploadListener = EventListener { event ->
            if (event is EventListener.Event.HeapAnalysisDone.HeapAnalysisSucceeded) {
                val heapAnalysis = event.heapAnalysis
                LeakCanaryUploadService().upload(heapAnalysis)
            }
        }

        LeakCanary.config = LeakCanary.config.run {
            copy(eventListeners = eventListeners + analysisUploadListener)
        }
    }
}


