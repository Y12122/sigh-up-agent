import { CheckOutlined, FileTextOutlined, ReloadOutlined, WarningOutlined } from "@ant-design/icons";
import { Button, Descriptions, Space, Tag, Typography } from "antd";
import { useState } from "react";

const fields = [
  { label: "姓名", value: "陈晓明", confidence: 98, state: "ok" },
  { label: "证件号", value: "A12***89", confidence: 72, state: "risk" },
  { label: "地址证明", value: "2026-03-18", confidence: 91, state: "blocking" },
  { label: "持股比例合计", value: "100%", confidence: 100, state: "ok" }
];

export function ReviewWorkbench() {
  const [selected, setSelected] = useState(fields[1]);
  return (
    <main className="review-workbench" id="main-content">
      <div className="review-titlebar">
        <div>
          <Typography.Text type="secondary">案件 HK-20260712-001</Typography.Text>
          <Typography.Title level={2}>恒星贸易有限公司</Typography.Title>
        </div>
        <Tag color="processing">待人工复核</Tag>
      </div>
      <div className="review-grid">
        <section className="document-pane" aria-label="材料预览" data-page="1">
          <div className="pane-heading"><FileTextOutlined /><strong>原始材料</strong><span>董事身份证 · 第 1 页</span></div>
          <div className="document-preview">
            <div className="document-sheet">
              <span>HONG KONG IDENTITY CARD</span>
              <strong>CHEN XIAOMING</strong>
              <span>A12***89</span>
            </div>
          </div>
        </section>
        <section className="field-pane" aria-labelledby="field-title">
          <div className="pane-heading"><strong id="field-title">结构化字段与风险</strong><span>4 个字段</span></div>
          <div className="field-list">
            {fields.map((field) => (
              <button className={`field-row ${selected.label === field.label ? "selected" : ""}`} key={field.label} onClick={() => setSelected(field)} aria-label={field.label === "证件号" ? "复核证件号" : `查看${field.label}`}>
                <div><span className="field-label">{field.label}</span><strong>{field.value}</strong></div>
                <Space>
                  {field.state === "ok" && <CheckOutlined className="status-ok" />}
                  {field.state === "risk" && <Tag color="warning">需确认</Tag>}
                  {field.state === "blocking" && <Tag color="error">需补件</Tag>}
                </Space>
              </button>
            ))}
          </div>
          <div className="field-detail">
            <Typography.Text type="secondary">{selected.label}</Typography.Text>
            <Typography.Title level={4}>{selected.value}</Typography.Title>
            <Tag color={selected.confidence < 80 ? "warning" : "success"}>OCR 置信度 {selected.confidence}%</Tag>
            {selected.state === "blocking" && <p className="risk-message"><WarningOutlined /> 地址证明已超过三个月</p>}
          </div>
          <Descriptions size="small" column={1} items={[{ key: "source", label: "来源", children: "客户上传 · OCR 候选" }, { key: "updated", label: "更新时间", children: "2026-07-12 11:30" }]} />
        </section>
      </div>
      <footer className="review-actions">
        <Button icon={<ReloadOutlined />}>退回补件</Button>
        <Button type="primary" icon={<CheckOutlined />}>复核通过</Button>
      </footer>
    </main>
  );
}
