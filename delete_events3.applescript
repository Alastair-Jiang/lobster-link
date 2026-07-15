tell application "Calendar"
    set coursePrefixes to {"高等数学(下)", "大学生心理健康教育", "中国近现代史纲要", "会计学", "英语精读2", "英语听说2", "应用写作", "形势与政策2", "马克思主义基本原理", "微观经济学", "劳动教育", "数据处理与程序设计", "习近平新时代中国特色社会主义思想概论", "线性代数"}
    
    set startDate to current date
    set month of startDate to March
    set day of startDate to 1
    set year of startDate to 2026
    
    set endDate to current date
    set month of endDate to July
    set day of endDate to 31
    set year of endDate to 2026
    
    set deletedCount to 0
    
    repeat with c in calendars
        try
            set targetEvents to (every event of c whose start date is greater than or equal to startDate and end date is less than or equal to endDate)
            repeat with e in targetEvents
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
