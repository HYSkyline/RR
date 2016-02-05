Attribute VB_Name = "Ä£¿é1"
Option Explicit

Sub align()
Dim row_num As Integer
Dim name_str As String
Dim i As Integer

Range("A1").Select
ActiveCell.Offset(0, 1).Range("A1").Select
Do Until ActiveCell.Value = ""
    If ActiveCell.Offset(0, 6).Value <> "" Then
        i = 0
        ActiveCell.Offset(0, -1).Range("A1").Select
        name_str = ActiveCell.Value + ActiveCell.Offset(0, 1).Value
        Debug.Print name_str + " ÅÅÁÐ´íÎó."
        
        ActiveCell.FormulaR1C1 = name_str
        Do Until ActiveCell.Value = ""
            ActiveCell.Offset(0, 1).Range("A1").Select
            ActiveCell.FormulaR1C1 = ActiveCell.Offset(0, 1).Value
            i = i + 1
        Loop
        ActiveCell.Offset(0, -i + 1).Range("A1").Select
    End If
    ActiveCell.Offset(1, 0).Range("A1").Select
Loop
End Sub

Sub month_transform()
Do Until ActiveCell.Value = ""
    If ActiveCell.Value = "Jan" Then
        ActiveCell.Value = "01"
    ElseIf ActiveCell.Value = "Feb" Then
        ActiveCell.Value = "02"
    ElseIf ActiveCell.Value = "Mar" Then
        ActiveCell.Value = "03"
    ElseIf ActiveCell.Value = "Apr" Then
        ActiveCell.Value = "04"
    ElseIf ActiveCell.Value = "May" Then
        ActiveCell.Value = "05"
    ElseIf ActiveCell.Value = "Jun" Then
        ActiveCell.Value = "06"
    ElseIf ActiveCell.Value = "Jul" Then
        ActiveCell.Value = "07"
    ElseIf ActiveCell.Value = "Aug" Then
        ActiveCell.Value = "08"
    ElseIf ActiveCell.Value = "Sep" Then
        ActiveCell.Value = "09"
    ElseIf ActiveCell.Value = "Oct" Then
        ActiveCell.Value = "10"
    ElseIf ActiveCell.Value = "Nov" Then
        ActiveCell.Value = "11"
    ElseIf ActiveCell.Value = "Dec" Then
        ActiveCell.Value = "12"
    Else
        ActiveCell.Value = "None"
    End If
    ActiveCell.Offset(1, 0).Range("A1").Select
Loop
End Sub

Sub weekday_transform()
Do Until ActiveCell.Value = ""
    If ActiveCell.Value = "Mon" Then
        ActiveCell.Value = "01"
    ElseIf ActiveCell.Value = "Tue" Then
        ActiveCell.Value = "02"
    ElseIf ActiveCell.Value = "Wed" Then
        ActiveCell.Value = "03"
    ElseIf ActiveCell.Value = "Thu" Then
        ActiveCell.Value = "04"
    ElseIf ActiveCell.Value = "Fri" Then
        ActiveCell.Value = "05"
    ElseIf ActiveCell.Value = "Sat" Then
        ActiveCell.Value = "06"
    ElseIf ActiveCell.Value = "Sun" Then
        ActiveCell.Value = "07"
    Else
        ActiveCell.Value = "None"
    End If
    ActiveCell.Offset(1, 0).Range("A1").Select
Loop
End Sub
