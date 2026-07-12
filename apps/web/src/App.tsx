import { SafetyCertificateOutlined } from "@ant-design/icons";
import { ConfigProvider, Layout, Segmented, Space, Typography } from "antd";
import { useState } from "react";

import { CustomerFlow } from "./features/customer/CustomerFlow";
import { CaseBoard } from "./features/review/CaseBoard";
import { ReviewWorkbench } from "./features/review/ReviewWorkbench";
import "./styles.css";

const { Header, Content } = Layout;
type View = "board" | "review" | "customer";

export function App() {
  const [view, setView] = useState<View>("board");
  return <ConfigProvider theme={{ token: { borderRadius: 6, colorPrimary: "#176b5b", colorInfo: "#176b5b" } }}>
    <Layout className="app-shell">
      <a className="skip-link" href="#main-content">跳到主要内容</a>
      <Header className="app-header">
        <Space><SafetyCertificateOutlined className="brand-icon" /><Typography.Title level={4}>工商注册工作台</Typography.Title></Space>
        <Segmented value={view === "customer" ? "customer" : "employee"} onChange={(value) => setView(value === "customer" ? "customer" : "board")} options={[{ label: "员工工作台", value: "employee" }, { label: "客户上传端", value: "customer" }]} />
      </Header>
      <Content>{view === "customer" ? <CustomerFlow /> : view === "review" ? <ReviewWorkbench /> : <CaseBoard onOpen={() => setView("review")} />}</Content>
    </Layout>
  </ConfigProvider>;
}

