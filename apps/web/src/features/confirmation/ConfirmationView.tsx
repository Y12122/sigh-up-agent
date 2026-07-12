import { CheckCircleOutlined, FilePdfOutlined, FileWordOutlined } from "@ant-design/icons";
import { Button, Checkbox, Descriptions, Result, Space, Table, Tag, Typography } from "antd";
import { useState } from "react";

interface Props { onConfirm?: () => void; }

export function ConfirmationView({ onConfirm = () => undefined }: Props) {
  const [acknowledged, setAcknowledged] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  if (confirmed) return <main className="confirmation-view" id="main-content"><Result status="success" title="注册信息已确认" subTitle="确认单版本 1 已锁定" /></main>;
  return <main className="confirmation-view" id="main-content">
    <div className="confirmation-heading">
      <div><Typography.Text type="secondary">确认单版本 1</Typography.Text><Typography.Title level={2}>注册信息确认</Typography.Title></div>
      <Tag color="processing">待客户确认</Tag>
    </div>
    <section className="confirmation-band">
      <Typography.Title level={4}>公司信息</Typography.Title>
      <Descriptions column={{ xs: 1, md: 2 }} items={[
        { key: "zh", label: "中文名称", children: "恒星贸易有限公司" },
        { key: "en", label: "英文名称", children: "GALAXY TRADING LIMITED" },
        { key: "scope", label: "经营范围", children: "国际贸易" },
        { key: "capital", label: "注册资本", children: "10,000.00 HKD" },
        { key: "address", label: "注册地址", children: "香港测试区示例道 1 号", span: 2 }
      ]} />
    </section>
    <section className="confirmation-band">
      <Typography.Title level={4}>董事与股东</Typography.Title>
      <Table pagination={false} rowKey="name" dataSource={[{ name: "测试董事甲", role: "董事 / 股东", shares: "100.00%", document: "MASKED-A001" }]} columns={[
        { title: "姓名", dataIndex: "name" }, { title: "角色", dataIndex: "role" }, { title: "持股", dataIndex: "shares" }, { title: "证件", dataIndex: "document" }
      ]} />
    </section>
    <div className="confirmation-downloads"><Space><Button icon={<FileWordOutlined />}>Word</Button><Button icon={<FilePdfOutlined />}>PDF</Button></Space></div>
    <div className="confirmation-action">
      <Checkbox checked={acknowledged} onChange={(event) => setAcknowledged(event.target.checked)}>我已核对以上注册信息，确认内容准确无误</Checkbox>
      <Button type="primary" icon={<CheckCircleOutlined />} disabled={!acknowledged} onClick={() => { onConfirm(); setConfirmed(true); }}>确认注册信息</Button>
    </div>
  </main>;
}
