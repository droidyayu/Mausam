package com.example.mausam.leak

import shark.LeakTrace

class ApplicationLeakException(
    leakTrace: LeakTrace, stackTraceElementList: MutableList<StackTraceElement>
) : LeakException(leakTrace, stackTraceElementList)
