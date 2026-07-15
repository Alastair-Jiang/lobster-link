tell application "Calendar"
    set courseNames to {"高等数学(下) (谢嘉宁)", "大学生心理健康教育 (李昊然)", "中国近现代史纲要 (宋正)", "会计学 (庄汶资)", "英语精读2 (马喜文)", "英语听说2 (王向红)", "应用写作 (周咏梅)", "形势与政策2 (丁涛)", "马克思主义基本原理 (王坤平)", "微观经济学 (谷雨)", "劳动教育 (赵晗)", "数据处理与程序设计 (陶永明)", "习近平新时代中国特色社会主义思想概论 (韩丹丹)", "线性代数 (张蕴资)"}
    
    set deletedCount to 0
    repeat with c in calendars
        try
            set targetEvents to (every event of c whose summary is in courseNames)
            repeat with e in targetEvents
                delete e
                set deletedCount to deletedCount + 1
            end repeat
        end try
    end repeat
    save
    return "Deleted " & deletedCount & " duplicated events."
end tell
