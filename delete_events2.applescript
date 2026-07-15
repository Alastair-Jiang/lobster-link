tell application "Calendar"
    set coursePrefixes to {"高等数学(下)", "大学生心理健康教育", "中国近现代史纲要", "会计学", "英语精读2", "英语听说2", "应用写作", "形势与政策2", "马克思主义基本原理", "微观经济学", "劳动教育", "数据处理与程序设计", "习近平新时代中国特色社会主义思想概论", "线性代数"}
    
    set deletedCount to 0
    repeat with c in calendars
        try
            set allEvents to every event of c
            repeat with e in allEvents
                set evtName to summary of e
                repeat with prefix in coursePrefixes
                    if evtName starts with prefix then
                        delete e
                        set deletedCount to deletedCount + 1
                        exit repeat
                    end if
                end repeat
            end repeat
        end try
    end repeat
    save
    return "Deleted " & deletedCount & " duplicated events."
end tell
