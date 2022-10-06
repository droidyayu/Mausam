package com.example.mausam.leak

import com.google.firebase.crashlytics.FirebaseCrashlytics
import shark.HeapAnalysis
import shark.HeapAnalysisSuccess
import shark.LeakTraceObject

class LeakCanaryUploadService {

    fun upload(heapAnalysis: HeapAnalysisSuccess) {
        captureApplicationLeaks(heapAnalysis)
        captureLibraryLeaks(heapAnalysis)
    }

    private fun captureApplicationLeaks(heapAnalysis: HeapAnalysisSuccess) {
        heapAnalysis
            .applicationLeaks
            .flatMap { leak ->
                leak.leakTraces.map { leakTrace -> leak to leakTrace }
            }.map { (_, leakTrace) ->
                val crashlytics = FirebaseCrashlytics.getInstance()
                crashlytics.recordException(
                    ApplicationLeakException(leakTrace, getStackTraceList(leakTrace.leakingObject)),
                )
            }
    }

    private fun captureLibraryLeaks(heapAnalysis: HeapAnalysisSuccess) {
        heapAnalysis
            .libraryLeaks
            .flatMap { leak ->
                leak.leakTraces.map { leakTrace -> leak to leakTrace }
            }.map { (_, leakTrace) ->
                val crashlytics = FirebaseCrashlytics.getInstance()
                crashlytics.recordException(
                    LibraryLeakException(leakTrace, getStackTraceList(leakTrace.leakingObject))
                )
            }
    }

    private fun getStackTraceList(
        leakTraceObject: LeakTraceObject,
        isApplicationLeak: Boolean = true
    ): MutableList<StackTraceElement> {
        val stackTraceList: MutableList<StackTraceElement> = mutableListOf()
        val defaultMessage = if (isApplicationLeak) {
            "Application Leak"
        } else {
            "Library Leak"
        }
        if (leakTraceObject.leakingStatus == LeakTraceObject.LeakingStatus.LEAKING) {
            stackTraceList.add(
                StackTraceElement(
                    leakTraceObject.leakingStatusReason,
                    "",
                    "$defaultMessage in ${leakTraceObject.className.split("\n")[0]}", 0
                )
            )
        } else {
            stackTraceList.add(StackTraceElement("", defaultMessage, "", 0))
        }
        return stackTraceList
    }
}
