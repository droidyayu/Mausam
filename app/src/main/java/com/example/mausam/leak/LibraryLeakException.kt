package com.example.mausam.leak

import shark.LeakTrace

class LibraryLeakException(
    leakTrace: LeakTrace, stackTraceElementList: MutableList<StackTraceElement>
) : LeakException(leakTrace, stackTraceElementList)